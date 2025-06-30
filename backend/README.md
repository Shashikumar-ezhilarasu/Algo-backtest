# FastAPI Backend for Option Backtest Clone

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