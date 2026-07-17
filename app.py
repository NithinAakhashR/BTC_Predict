from flask import Flask, render_template, request, jsonify
print("Flask imported")
import numpy as np
print("Numpy imported")
import pandas as pd
print("Pandas imported")
import yfinance as yf
print("Yfinance imported")
from sklearn.preprocessing import MinMaxScaler
print("Sklearn imported")
# TensorFlow Keras is used for saved model compatibility
from tensorflow.keras.models import load_model
print("TensorFlow Keras loaded")
from datetime import datetime, timedelta
import traceback
import google.generativeai as genai
print("GenAI imported")
import os

app = Flask(__name__)
print("App initialized")

# Load both models (lazy loading to allow server start even if training)
model_daily = None
model_hourly = None

def get_models():
    global model_daily, model_hourly
    print("get_models: current cwd=", os.getcwd())
    print("get_models: daily path=", os.path.abspath("bitcoin_lstm_model_daily.h5"))
    print("get_models: hourly path=", os.path.abspath("bitcoin_lstm_model_hourly.h5"))
    if model_daily is None:
        print("get_models: loading daily model")
        try:
            model_daily = load_model("bitcoin_lstm_model_daily.h5")
            print("get_models: daily model loaded")
        except Exception as e:
            print(f"Error loading daily model: {e}")
            traceback.print_exc()
            pass
    if model_hourly is None:
        print("get_models: loading hourly model")
        try:
            model_hourly = load_model("bitcoin_lstm_model_hourly.h5")
            print("get_models: hourly model loaded")
        except Exception as e:
            print(f"Error loading hourly model: {e}")
            traceback.print_exc()
            pass

def compute_rsi(prices, period=14):
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50).values


def compute_macd(prices, slow=26, fast=12, signal=9):
    prices_series = pd.Series(prices)
    exp1 = prices_series.ewm(span=fast, adjust=False).mean()
    exp2 = prices_series.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line.values, signal_line.values, histogram.values


def build_explanation(data, predicted_prices, interval):
    if isinstance(data.columns, pd.MultiIndex):
        close = data['Close']['BTC-USD'].dropna()
        volume = data['Volume']['BTC-USD'].dropna()
    else:
        close = data['Close'].dropna()
        volume = data['Volume'].dropna()

    last_close = float(close.iloc[-1])
    predicted_last = float(predicted_prices[-1])
    price_dir = 'increased' if predicted_last >= last_close else 'decreased'

    rsi_values = compute_rsi(close.values, period=14)
    rsi = float(rsi_values[-1]) if len(rsi_values) > 0 else 50.0

    ma_period = 20 if interval == '1d' else 12
    moving_average = float(close.rolling(window=ma_period, min_periods=1).mean().iloc[-1])

    macd_line, signal_line, _ = compute_macd(close.values)
    macd = float(macd_line[-1])
    signal = float(signal_line[-1])

    volume_avg = float(volume.rolling(window=ma_period, min_periods=1).mean().iloc[-1])
    volume_trend = 'rising' if float(volume.iloc[-1]) >= volume_avg else 'falling'

    reasons = []
    if rsi >= 70:
        reasons.append('RSI indicates overbought pressure')
    elif rsi >= 55:
        reasons.append('RSI indicates bullish momentum')
    elif rsi <= 30:
        reasons.append('RSI indicates oversold conditions')
    else:
        reasons.append('RSI is neutral')

    if last_close >= moving_average:
        reasons.append(f'price remains above its {ma_period}-period moving average')
    else:
        reasons.append(f'price remains below its {ma_period}-period moving average')

    if macd > signal:
        reasons.append('MACD is positive versus its signal line')
    else:
        reasons.append('MACD is below its signal line')

    reasons.append(f'trading volume is {volume_trend}')

    explanation = f"Prediction {price_dir} because {', '.join(reasons)}."
    return explanation


def predict_future(interval, period, model, steps_ahead, lookback=60):
    print(f"predict_future: interval={interval}, period={period}")
    data = yf.download("BTC-USD", period=period, interval=interval)
    print(f"predict_future: data shape={data.shape}")
    
    if data.empty:
        print("predict_future: data is empty!")
        raise Exception("Yahoo Finance returned empty data. Check your connection or the ticker.")

    if isinstance(data.columns, pd.MultiIndex):
        bitcoin_prices = data["Close"]["BTC-USD"].dropna().values
    else:
        bitcoin_prices = data["Close"].dropna().values
        
    dates = data.index.strftime("%Y-%m-%d %H:%M:%S" if interval == '1h' else "%Y-%m-%d").tolist()
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(bitcoin_prices).reshape(-1, 1))
    
    last_window = scaled_data[-lookback:].reshape(1, lookback, 1)
    predictions = []
    current_input = last_window.copy()
    
    for _ in range(steps_ahead):
        pred = model.predict(current_input, verbose=0)
        predictions.append(pred[0][0])
        current_input = np.append(current_input[:, 1:, :], [[[pred[0][0]]]], axis=1)
        
    predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten().tolist()
    
    last_prices = bitcoin_prices[-lookback:].tolist()
    last_dates = dates[-lookback:]
    
    last_date = data.index[-1]
    
    future_dates = []
    for i in range(1, steps_ahead + 1):
        if interval == '1h':
            next_date = last_date + timedelta(hours=i)
            future_dates.append(next_date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            next_date = last_date + timedelta(days=i)
            future_dates.append(next_date.strftime("%Y-%m-%d"))
            
    explanation = build_explanation(data, predicted_prices, interval)
    return last_dates, last_prices, future_dates, predicted_prices, explanation


def generate_dummy_forecast(last_prices, steps_ahead):
    if len(last_prices) == 0:
        return [0.0] * steps_ahead
    if len(last_prices) < 2:
        return [float(last_prices[-1])] * steps_ahead
    trend = np.mean(np.diff(last_prices[-7:])) if len(last_prices) >= 7 else np.mean(np.diff(last_prices))
    return [float(last_prices[-1] + trend * (i + 1)) for i in range(steps_ahead)]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict_daily", methods=["POST"])
def predict_daily():
    try:
        get_models()
        if model_daily is not None:
            last_dates, last_prices, future_dates, predicted_prices, explanation = predict_future(
                interval="1d", period="5y", model=model_daily, steps_ahead=7
            )
        else:
            print("Daily model unavailable, using fallback forecast")
            data = yf.download("BTC-USD", period="5y", interval="1d")
            if data.empty:
                return jsonify({"success": False, "error": "Could not fetch latest data."})
            if isinstance(data.columns, pd.MultiIndex):
                close_prices = data["Close"]["BTC-USD"].dropna().values.tolist()
            else:
                close_prices = data["Close"].dropna().values.tolist()
            last_dates = data.index.strftime("%Y-%m-%d").tolist()[-60:]
            last_prices = close_prices[-60:]
            future_dates = [(data.index[-1] + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
            predicted_prices = generate_dummy_forecast(last_prices, 7)
            explanation = "Model failed to load due to compatibility issues. Showing a trend-based fallback forecast."

        return jsonify({
            "success": True,
            "history": {"dates": last_dates, "prices": last_prices},
            "prediction": {"dates": future_dates, "prices": predicted_prices},
            "explanation": explanation
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route("/predict_hourly", methods=["POST"])
def predict_hourly():
    try:
        get_models()
        if model_hourly is not None:
            last_dates, last_prices, future_dates, predicted_prices, explanation = predict_future(
                interval="1h", period="730d", model=model_hourly, steps_ahead=24
            )
        else:
            print("Hourly model unavailable, using fallback forecast")
            data = yf.download("BTC-USD", period="730d", interval="1h")
            if data.empty:
                return jsonify({"success": False, "error": "Could not fetch latest data."})
            if isinstance(data.columns, pd.MultiIndex):
                close_prices = data["Close"]["BTC-USD"].dropna().values.tolist()
            else:
                close_prices = data["Close"].dropna().values.tolist()
            last_dates = data.index.strftime("%Y-%m-%d %H:%M:%S").tolist()[-60:]
            last_prices = close_prices[-60:]
            future_dates = [(data.index[-1] + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(1, 25)]
            predicted_prices = generate_dummy_forecast(last_prices, 24)
            explanation = "Model failed to load due to compatibility issues. Showing a trend-based fallback forecast."

        return jsonify({
            "success": True,
            "history": {"dates": last_dates, "prices": last_prices},
            "prediction": {"dates": future_dates, "prices": predicted_prices},
            "explanation": explanation
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    api_key = "AIzaSyBkGqKqKaM3DH_xi4qRLCnNPFK084ZeX1s"

    if not api_key:
        return jsonify({"success": False, "error": "Please set your Gemini API key."})
        
    try:
        genai.configure(api_key=api_key)
        
        # Dynamically find a supported model to prevent 404 errors
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        model_name = None
        preferred_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro', 'models/gemini-1.5-pro-latest', 'models/gemini-pro', 'models/gemini-1.0-pro']
        
        for pref in preferred_models:
            if pref in available_models:
                model_name = pref
                break
                
        if not model_name:
            if available_models:
                model_name = available_models[0]
            else:
                return jsonify({"success": False, "error": "No supported models found for this API key."})

        # Load CSV and calculate some basic stats for the model to use
        # The CSV has some metadata rows, so we handle them
        df = pd.read_csv("bitcoin_prices.csv", skiprows=[1, 2])
        # Ensure Close column is numeric
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df = df.dropna(subset=['Close'])
        
        current_price = df['Close'].iloc[-1]
        start_price_5y = df['Close'].iloc[0] if len(df) > 1825 else df['Close'].iloc[0]
        growth_5y = (float(current_price) / float(start_price_5y)) ** (1/5) - 1 # Annualized growth rate
        
        system_msg = f"""You are a helpful Bitcoin Forecasting Expert. 
        You have access to historical Bitcoin price data.
        
        Current Price: ${current_price:,.2f}
        Historical Annualized Growth Rate (estimated): {growth_5y:.2%}
        
        When asked for predictions for the upcoming days, weeks, months, or years (up to 5 years):
        1. Use the historical annualized growth rate as a baseline.
        2. Provide predictions broken down by:
           - Specific Dates and Days (for the immediate next 7 days)
           - Weekly projections (for the next month)
           - Monthly projections (for the next year)
           - Yearly projections (for the next 5 years)
        3. Structure your response with clear tables and bold headings.
        4. Always mention that these are AI-assisted projections based on historical data and not financial advice.
        5. Extract specific historical dates/prices from the CSV content when asked.
        """
        
        if '1.5' in model_name:
            model = genai.GenerativeModel(model_name, system_instruction=system_msg)
            prompt = ""
        else:
            model = genai.GenerativeModel(model_name)
            prompt = f"System Instruction: {system_msg}\n\n"
        
        with open("bitcoin_prices.csv", "r") as f:
            csv_content = f.read()
            
        prompt += f"Historical Data (CSV format):\n{csv_content}\n\nUser Question: {message}"
        response = model.generate_content(prompt)
        
        return jsonify({"success": True, "reply": response.text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route("/simulate_scenario", methods=["POST"])
def simulate_scenario():
    try:
        scenario = request.json.get("scenario")
        get_models()
        
        # Get baseline 7-day forecast
        data = yf.download("BTC-USD", period="90d", interval="1d")
        if data.empty: return jsonify({"success": False, "error": "Could not fetch latest data."})
        
        if isinstance(data.columns, pd.MultiIndex):
            close_prices = data['Close']['BTC-USD'].dropna().values
        else:
            close_prices = data['Close'].dropna().values
            
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(close_prices.reshape(-1,1))
        
        last_60 = scaled_data[-60:]
        if len(last_60) < 60:
            last_60 = np.pad(last_60, ((60 - len(last_60), 0), (0, 0)), 'edge')
        input_seq = last_60.reshape(1, 60, 1)
        
        baseline = []
        if model_daily is not None:
            curr_seq = input_seq.copy()
            for _ in range(7):
                pred = model_daily.predict(curr_seq, verbose=0)
                baseline.append(float(scaler.inverse_transform(pred)[0][0]))
                curr_seq = np.append(curr_seq[:, 1:, :], pred.reshape(1,1,1), axis=1)
        else:
            last_prices_raw = close_prices[-60:].tolist()
            trend = np.mean(np.diff(last_prices_raw[-7:])) if len(last_prices_raw) >= 7 else 0
            baseline = [float(last_prices_raw[-1] + trend * (i + 1)) for i in range(7)]
            
        # Apply Scenario logic
        simulated = []
        if scenario == 'halving':
            simulated = [v * (1.02 ** (i+1)) for i, v in enumerate(baseline)]
            insight_prompt = "Explain the impact of a Bitcoin Halving event on price and supply scarcity in 2 sentences."
        elif scenario == 'etf':
            simulated = [v * 1.15 for v in baseline]
            insight_prompt = "Explain why institutional ETF approvals lead to massive capital inflows and price appreciation for Bitcoin in 2 sentences."
        elif scenario == 'crash':
            simulated = [v * 0.75 for v in baseline]
            insight_prompt = "Explain what causes a crypto flash crash and the liquidity drain that follows in 2 sentences."
        elif scenario == 'regulation':
            simulated = [v * (0.95 ** (i+1)) for i, v in enumerate(baseline)]
            insight_prompt = "Explain how strict government regulations or bans impact Bitcoin market liquidity and user adoption in 2 sentences."
        else:
            return jsonify({"success": False, "error": "Invalid scenario."})
            
        # Get AI Insight using dynamic model lookup
        api_key = "AIzaSyBkGqKqKaM3DH_xi4qRLCnNPFK084ZeX1s"
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']
        model_name = next((p for p in preferred if p in available_models), available_models[0] if available_models else None)
        if model_name:
            ai_model = genai.GenerativeModel(model_name)
            ai_resp = ai_model.generate_content(f"You are a crypto expert. {insight_prompt}")
            insight = ai_resp.text if ai_resp else "Scenario simulated based on historical volatility patterns."
        else:
            insight = "Scenario simulated based on historical volatility patterns."
        
        dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(7)]
        
        return jsonify({
            "success": True,
            "dates": dates,
            "baseline": baseline,
            "simulated": simulated,
            "insight": insight
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=False)
