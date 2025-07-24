<<<<<<< HEAD
## About

**Algo-backtest** is a Python-based backtesting framework designed for analyzing and evaluating trading strategies using historical market and trade data. The project provides tools to simulate trading strategies on options data, enabling users to assess performance, optimize parameters, and gain insights before deploying strategies in live markets.

### Key Features

- **Historical Data Analysis:** Supports CSV and Excel formats for market and trade data.
- **Strategy Simulation:** Run and evaluate trading strategies on historical options data.
- **Extensible Framework:** Modular design for easy integration of new strategies and data sources.
- **Results Visualization:** Tools for analyzing and visualizing backtest results (customizable).

### Project Structure

- `backend/`: Core logic, data handling, and models.
- `resources/`: Sample datasets and utility scripts for testing and optimization.
  
=======
# 🚀 Advanced Stock Market Backtesting Platform

A comprehensive stock market backtesting web application that simulates trading strategies over years of historical data within seconds. The platform provides detailed performance reports and integrates advanced features for realistic trading simulation.

## ✨ Features

### 🎯 Advanced Trading Features
- **Leg-wise Stop Loss**: Sophisticated stop loss management for complex strategies
- **Trailing Lock Profit**: Dynamic profit locking mechanism that follows favorable price movements
- **Re-entry Logic**: Intelligent re-entry system with immediate or delayed modes
- **Technical Indicators**: Built-in EMA and RSI indicators with customizable parameters
- **Market Hours Filtering**: Trade only during specified market hours

### 📊 Performance Analytics
- **Max Drawdown Analysis**: Comprehensive drawdown tracking and visualization
- **Success Rate Calculation**: Win/loss ratios with detailed statistics
- **Profit Factor**: Risk-adjusted performance metrics
- **Sharpe Ratio**: Risk-adjusted return calculations
- **Win/Loss Distribution**: Statistical analysis of trade outcomes

### 💰 Realistic Trading Simulation
- **Slippage Modeling**: Realistic price impact simulation
- **Brokerage Fees**: Configurable transaction costs
- **Tax Implications**: Automatic tax calculations on profits
- **Position Sizing**: Flexible position size management
- **Daily Loss Limits**: Risk management with daily stop-loss limits

### 🖥️ User Interface
- **Modern Streamlit Frontend**: Intuitive web interface with real-time updates
- **Interactive Charts**: Plotly-powered visualizations for comprehensive analysis
- **Strategy Management**: Save, load, and manage multiple trading strategies
- **Export Capabilities**: Download results in CSV format
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Charting**: Plotly
- **Data Processing**: Pandas, NumPy
- **Technical Analysis**: TA-Lib

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd backtest2
```

### 2. Database Setup
Make sure PostgreSQL is running and create a database:
```sql
CREATE DATABASE newbacktest;
```

Update database credentials in `backend/db.py` if needed.

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Start the Platform
```bash
./start_platform.sh
```

Or manually start both services:

**Start Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Start Frontend:**
```bash
python -m streamlit run streamlit_app.py --server.port 8501
```

### 5. Access the Application
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## 📊 Usage Guide

### 1. Data Upload
1. Navigate to the "📊 Backtest" page
2. Upload your market data file (CSV format)
3. Upload your trade signals file (CSV/XLSX format)

### 2. Strategy Configuration
Configure your backtesting parameters:

#### Basic Parameters
- **Stop Loss (%)**: Risk management stop loss percentage
- **Target Profit (%)**: Profit taking target percentage
- **Trading Hours**: Market session start and end times

#### Advanced Features
- **Trailing Stop Loss**: 
  - Enable trailing stop functionality
  - Set trigger percentage and lock percentage
- **Re-entry Logic**:
  - Enable multiple entries per signal
  - Choose immediate or delayed re-entry mode
  - Set maximum number of re-entries

#### Risk Management
- **Position Size**: Number of shares/contracts per trade
- **Slippage**: Price impact simulation (₹)
- **Brokerage**: Transaction costs per trade (₹)
- **Tax Rate**: Tax percentage on profits
- **Daily Loss Limit**: Maximum loss allowed per day

### 3. Run Backtest
Click "🚀 Run Backtest" to execute the strategy simulation.

### 4. Analyze Results
Review comprehensive performance metrics:
- **P&L Summary**: Total profit/loss with breakdown
- **Trade Statistics**: Win rate, average win/loss, trade count
- **Risk Metrics**: Maximum drawdown, Sharpe ratio, VaR
- **Charts**: Equity curve, P&L distribution, monthly performance
- **Trade Log**: Detailed record of all trades

### 5. Strategy Management
- **Save Strategy**: Store successful configurations for future use
- **Load Strategy**: Retrieve and reuse previously saved strategies
- **Export Results**: Download detailed trade logs and reports

## 📁 Data Format Requirements

### Market Data File (CSV)
Required columns:
- `Date`: Date in DD/MM/YYYY format
- `Time`: Time in HH:MM format
- `Open`: Opening price
- `High`: Highest price
- `Low`: Lowest price
- `Close`: Closing price

Example:
```csv
Date,Time,Open,High,Low,Close
01/04/2020,09:15,100.50,101.25,100.00,100.75
01/04/2020,09:16,100.75,101.00,100.25,100.50
```

### Trade Signals File (CSV/XLSX)
Configure based on your signal generation logic. The platform supports various signal formats and can be customized for specific requirements.

## 🔧 Configuration

### Database Configuration
Update `backend/db.py` with your PostgreSQL credentials:
```python
def get_conn():
    return psycopg2.connect(
        host="localhost",
        database="newbacktest",
        user="your_username",
        password="your_password"
    )
```

### API Configuration
Update the backend URL in `streamlit_app.py` if running on different servers:
```python
BACKEND_URL = "http://localhost:8000"
```

## 🔍 API Endpoints

The FastAPI backend provides the following endpoints:

- `POST /upload/tradefile`: Upload trade signals file
- `POST /upload/marketdata`: Upload market data file
- `POST /backtest/run`: Execute backtest with configuration
- `POST /strategy/save`: Save strategy configuration
- `GET /strategy/{name}`: Retrieve saved strategy
- `POST /strategy/{name}/retry`: Re-run saved strategy

Full API documentation is available at: http://localhost:8000/docs

## 🧪 Testing

The platform includes realistic simulation of:
- **Market Impact**: Slippage calculations based on position size
- **Transaction Costs**: Brokerage fees and taxes
- **Risk Controls**: Daily loss limits and position sizing
- **Market Hours**: Trading only during specified hours
- **Re-entry Logic**: Sophisticated re-entry mechanisms

## 📈 Performance Metrics Explained

### Key Metrics
- **Total P&L**: Net profit/loss after all costs
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **VaR (Value at Risk)**: Potential loss at confidence levels

### Risk Analysis
- **Consecutive Losses**: Maximum number of consecutive losing trades
- **Monthly Analysis**: Performance breakdown by month
- **Hourly Patterns**: Time-based performance analysis
- **Drawdown Periods**: Duration and magnitude of losing streaks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the configuration sections above
3. Ensure all prerequisites are installed correctly
4. Verify database connectivity

## 🔮 Future Enhancements

- **Multi-timeframe Analysis**: Support for different chart timeframes
- **Portfolio Backtesting**: Test multiple strategies simultaneously
- **Monte Carlo Simulation**: Statistical scenario analysis
- **Machine Learning Integration**: AI-powered strategy optimization
- **Real-time Data Integration**: Live market data connectivity
- **Mobile App**: Native mobile application
- **Cloud Deployment**: Scalable cloud infrastructure

---

**Built with ❤️ for traders and quantitative analysts**
>>>>>>> 13f8f55 (feat : added streamlit frontend)
