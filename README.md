# Bitcoin Price Prediction Dashboard

## 📊 Project Overview

A sophisticated web-based Bitcoin price prediction platform built with LSTM neural networks, featuring real-time forecasting, scenario simulations, AI-powered insights, and voice assistant capabilities. This institutional-grade tool provides 7-day daily forecasts and 24-hour hourly predictions with explainable AI analysis.

## ✨ Key Features

### 🔮 Forecasting Engine
- **Daily Forecast**: 7-day price predictions using LSTM models
- **Hourly Forecast**: 24-hour granular predictions
- **Real-time Data**: Live Bitcoin price data via Yahoo Finance API
- **Explainable AI**: Technical indicators (RSI, MACD, Moving Averages) with natural language explanations

### 🎯 Scenario Simulator
- **Bitcoin Halving Impact**: Supply shock simulation
- **Institutional ETF Approval**: Capital inflow modeling
- **Global Market Crash**: Liquidity drain analysis
- **Regulatory Crackdown**: Policy restriction impact
- **AI-Powered Insights**: Gemini AI-generated scenario analysis

### 🤖 AI Assistant
- **Chat Interface**: Natural language queries about Bitcoin data
- **Voice Assistant**: Browser-based speech recognition and synthesis
- **Data Analysis**: Historical trend analysis and market insights

### 🎨 User Interface
- **Dark Futuristic Theme**: Cyberpunk-inspired design
- **Interactive Charts**: ECharts-powered visualizations
- **Responsive Design**: Mobile and desktop optimized
- **Real-time Updates**: Dynamic data visualization

## 🛠️ Technology Stack

### Backend
- **Python Flask**: Web framework for API endpoints
- **TensorFlow/Keras**: LSTM model loading and inference
- **Google Generative AI**: Chat and scenario analysis
- **Yahoo Finance API**: Real-time market data
- **Scikit-learn**: Data preprocessing

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript (ES6+)**: Interactive functionality
- **ECharts**: Advanced charting library
- **Web Speech API**: Voice recognition and synthesis
- **Marked.js**: Markdown rendering

### Data Processing
- **NumPy/Pandas**: Numerical computing and data manipulation
- **Technical Indicators**: RSI, MACD, Moving Averages, Volume analysis

## 📋 Prerequisites

- Python 3.8+
- Node.js (optional, for development)
- Modern web browser with Web Speech API support (Chrome/Edge recommended)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Bitcoin Price Prediction"
```

### 2. Set up Virtual Environment
```bash
# Windows PowerShell
.\venv2\Scripts\Activate.ps1

# Windows Command Prompt
.\venv2\Scripts\activate.bat

# Linux/Mac
source venv2/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Pre-trained Models
Place the following model files in the project root:
- `bitcoin_lstm_model_daily.h5`
- `bitcoin_lstm_model_hourly.h5`

### 5. Configure API Keys
Update the Gemini API key in `app.py`:
```python
api_key = "your-gemini-api-key-here"
```

## 🎯 Usage

### Running the Application
```bash
python app.py
```

Access the dashboard at: `http://127.0.0.1:5000`

### Basic Workflow
1. **Select Forecast Type**: Choose between Daily (7 days) or Hourly (24 hours)
2. **Generate Prediction**: Click the forecast button to run LSTM model
3. **View Results**: Interactive chart with historical data and predictions
4. **Analyze Insights**: Read AI-generated explanations based on technical indicators
5. **Run Simulations**: Test various market scenarios and their potential impacts
6. **Use Voice Assistant**: Speak commands for hands-free operation

### Voice Commands
- "Show daily forecast"
- "Show hourly forecast"
- "Simulate halving scenario"
- "Simulate ETF approval"
- "Ask about Bitcoin trends"

## 📡 API Documentation

### Endpoints

#### `GET /`
Returns the main dashboard interface.

#### `POST /predict_daily`
Generates 7-day Bitcoin price forecast.

**Response:**
```json
{
  "success": true,
  "history": {
    "dates": ["2024-01-01", ...],
    "prices": [45000.0, ...]
  },
  "prediction": {
    "dates": ["2024-01-08", ...],
    "prices": [47000.0, ...]
  },
  "explanation": "Prediction explanation text..."
}
```

#### `POST /predict_hourly`
Generates 24-hour Bitcoin price forecast.

**Response:** Similar to `/predict_daily` but with hourly data.

#### `POST /chat`
Processes natural language queries about Bitcoin data.

**Request:**
```json
{
  "message": "What are the current market trends?"
}
```

**Response:**
```json
{
  "success": true,
  "reply": "AI-generated response..."
}
```

#### `POST /simulate_scenario`
Runs market scenario simulations.

**Request:**
```json
{
  "scenario": "halving"
}
```

**Response:**
```json
{
  "success": true,
  "dates": ["2024-01-01", ...],
  "baseline": [45000.0, ...],
  "simulated": [47000.0, ...],
  "insight": "AI analysis of scenario impact..."
}
```

## 📁 Project Structure

```
Bitcoin Price Prediction/
├── app.py                          # Flask application
├── bitcoin_prices.csv             # Historical data
├── bitcoin_lstm_model_daily.h5    # Daily prediction model
├── bitcoin_lstm_model_hourly.h5   # Hourly prediction model
├── check_deps.py                  # Dependency checker
├── btc_price_prediction.py        # Prediction utilities
├── update_data.py                 # Data update script
├── test_flask.py                  # Flask tests
├── templates/
│   └── index.html                 # Main dashboard
├── static/
│   ├── style.css                  # Styling
│   └── bitcoin_logo.png           # Logo asset
└── venv2/                         # Virtual environment
```

## 🔧 Configuration

### Model Training
The LSTM models were trained on 5+ years of historical Bitcoin data with:
- 60-day lookback window
- Technical indicators as features
- MinMax scaling for normalization
- Adam optimizer with MSE loss

### API Keys
- **Gemini AI**: Required for chat and scenario analysis
- **Yahoo Finance**: No API key required (public access)

## 🧪 Testing

### Running Tests
```bash
python test_flask.py
```

### Manual Testing
1. Import check: `python -c "import app; print('OK')"`
2. Model loading: `python -c "import app; app.get_models(); print('Models loaded')"`
3. API endpoints: Use Postman or curl to test endpoints

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://127.0.0.1:5000
```

### Production Deployment
1. Set up production WSGI server (Gunicorn)
2. Configure reverse proxy (Nginx)
3. Set environment variables for API keys
4. Enable HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper documentation
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Yahoo Finance for market data
- Google for Gemini AI
- TensorFlow/Keras for ML framework
- ECharts for visualization
- Flask community for web framework

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub

---

**Note**: This is an educational project demonstrating AI/ML applications in financial forecasting. Not intended for actual investment decisions. Always conduct your own research and consult financial advisors.</content>
<parameter name="filePath">c:\Users\abcom\Desktop\Bitcoin_Prediction\Bitcoin-Price-Prediction\Bitcoin Price Prediction\README.md