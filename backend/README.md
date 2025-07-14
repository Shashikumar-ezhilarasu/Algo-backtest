# FastAPI Backend for Option Backtest Clone

## About

**Backtest2** is a Python-based backtesting framework designed for analyzing and evaluating trading strategies using historical market and trade data. The project provides tools to simulate trading strategies on options data, enabling users to assess performance, optimize parameters, and gain insights before deploying strategies in live markets.

### Key Features

- **Historical Data Analysis:** Supports CSV and Excel formats for market and trade data.
- **Strategy Simulation:** Run and evaluate trading strategies on historical options data.
- **Extensible Framework:** Modular design for easy integration of new strategies and data sources.
- **Results Visualization:** Tools for analyzing and visualizing backtest results (customizable).

### Project Structure

- `backend/`: Core logic, data handling, and models.
- `resources/`: Sample datasets and utility scripts for testing and optimization.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

3. Endpoints:
   - `POST /upload/tradefile` (upload .xlsx)
   - `POST /upload/marketdata` (upload .csv)
   - `POST /backtest/run` (run backtest)
   - `POST /strategy/save` (save config)
   - `GET /strategy/{name}` (load config)

4. Make sure your PostgreSQL is running and accessible with the credentials in `db.py`. 