import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import datetime
import os

def train_model(interval, period, model_filename, lookback=60, epochs=10):
    print(f"Training {interval} model over {period}...")
    
    # Fetch data
    data = yf.download("BTC-USD", period=period, interval=interval)
    
    # Handle multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data["Close"]["BTC-USD"]
    else:
        close_data = data["Close"]
        
    close_data = close_data.dropna().values
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(close_data).reshape(-1, 1))
    
    X_train, y_train = [], []
    for i in range(lookback, len(scaled_data)):
        X_train.append(scaled_data[i-lookback:i, 0])
        y_train.append(scaled_data[i, 0])
        
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X_train, y_train, epochs=epochs, batch_size=32)
    
    model.save(model_filename)
    print(f"Saved {model_filename}")

if __name__ == "__main__":
    # Train Daily Model (5 years)
    train_model(interval="1d", period="5y", model_filename="bitcoin_lstm_model_daily.h5", epochs=10)
    
    # Train Hourly Model (730 days)
    train_model(interval="1h", period="730d", model_filename="bitcoin_lstm_model_hourly.h5", epochs=10)
