import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from db import save_strategy, get_strategy
from models import BacktestConfig, BacktestResult
from typing import Optional
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# App setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_DIR = os.path.join(BASE_DIR, "data", "trades")
MARKET_DIR = os.path.join(BASE_DIR, "data", "market")

os.makedirs(TRADE_DIR, exist_ok=True)
os.makedirs(MARKET_DIR, exist_ok=True)

# Upload endpoints
@app.post("/upload/tradefile")
async def upload_tradefile(file: UploadFile = File(...)):
    file_path = os.path.join(TRADE_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@app.post("/upload/marketdata")
async def upload_marketdata(file: UploadFile = File(...)):
    file_path = os.path.join(MARKET_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

# Utility functions
def calculate_strike(spot: float, n: int, kind: str) -> float:
    atm = round(spot / 50) * 50
    if kind == 'ATM':
        return atm
    elif kind == 'OTM':
        return atm + (50 * n)
    elif kind == 'ITM':
        return atm - (50 * n)
    else:
        return atm

def get_expiry(date, expiry_mode, market_df):
    date = pd.to_datetime(date, dayfirst=True)
    if expiry_mode == 'weekly':
        thursdays = market_df[market_df['Date'].apply(lambda d: pd.to_datetime(d, dayfirst=True).weekday() == 3)]
        next_thurs = thursdays[thursdays['Date'] >= date.strftime('%d/%m/%Y')]['Date'].unique()
        return next_thurs[0] if len(next_thurs) > 0 else None
    elif expiry_mode == 'monthly':
        month = date.month
        thursdays = market_df[market_df['Date'].apply(lambda d: pd.to_datetime(d, dayfirst=True).weekday() == 3 and pd.to_datetime(d, dayfirst=True).month == month)]
        if not thursdays.empty:
            return thursdays['Date'].iloc[-1]
    return None

# Backtest engine
@app.post("/backtest/run", response_model=BacktestResult)
def run_backtest(config: BacktestConfig):
    trade_path = os.path.join(TRADE_DIR, config.tradefile)
    market_path = os.path.join(MARKET_DIR, config.marketfile)

    if not os.path.exists(trade_path) or not os.path.exists(market_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Read and preprocess market data
    market = pd.read_csv(market_path)
    market.columns = [c.strip() for c in market.columns]
    
    # Convert date and time
    market['Date'] = pd.to_datetime(market['Date'], dayfirst=True).dt.strftime('%Y-%m-%d')
    market['Time'] = pd.to_datetime(market['Time'], format='%H:%M:%S').dt.strftime('%H:%M')
    
    # Convert price columns to numeric, handling commas
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        market[col] = market[col].astype(str).str.replace(',', '').astype(float)

    # Add technical indicators
    market['EMA20'] = EMAIndicator(close=market['Close'], window=20).ema_indicator()
    market['RSI'] = RSIIndicator(close=market['Close'], window=14).rsi()
    
    # Drop rows with NaN values from indicators
    market.dropna(inplace=True)

    trade_log = []
    equity_curve = []
    balance = 0
    reentry_tracker = {}

    # Time filter setup
    start_time = getattr(config, 'start_time', '09:15')
    end_time = getattr(config, 'end_time', '15:15')

    for i in range(len(market)):
        row = market.iloc[i]
        date, time = row['Date'], row['Time']

        # Apply time filter
        if time < start_time or time > end_time:
            continue

        # Get technical indicator values
        ema = row['EMA20']
        rsi = row['RSI']
        close = row['Close']

        # Generate signals
        long_signal = ema < close and rsi > 50
        short_signal = ema > close and rsi < 50

        if not long_signal and not short_signal:
            continue

        # Check for both LONG and SHORT opportunities
        for direction in ['LONG', 'SHORT']:
            if (direction == 'LONG' and not long_signal) or (direction == 'SHORT' and not short_signal):
                continue

            # Check reentry conditions
            key = f"{date}_{direction}"
            if key in reentry_tracker:
                if reentry_tracker[key]['count'] >= config.reentry_count:
                    continue
                if config.reentry_mode == 'RE-DELAYED':
                    if i < reentry_tracker[key]['next_entry']:
                        continue

            # Initialize trade parameters
            entry_price = close
            sl_price = entry_price * (1 - config.sl_pct / 100) if direction == 'LONG' else entry_price * (1 + config.sl_pct / 100)
            target_price = entry_price * (1 + config.target_pct / 100) if direction == 'LONG' else entry_price * (1 - config.target_pct / 100)
            
            trail_active = False
            trail_price = None
            trigger_pct = config.trail_trigger / 100 if config.trail_trigger else None
            lock_pct = config.trail_lock / 100 if config.trail_lock else None
            max_profit_pct = 0

            # Simulate trade
            for j in range(i + 1, len(market)):
                fut = market.iloc[j]
                fut_high = fut['High']
                fut_low = fut['Low']
                fut_time = fut['Time']

                if direction == 'LONG':
                    # Check for trailing stop activation
                    if trigger_pct and lock_pct:
                        curr_profit_pct = (fut_high - entry_price) / entry_price
                        if curr_profit_pct > max_profit_pct:
                            max_profit_pct = curr_profit_pct
                            if not trail_active and curr_profit_pct >= trigger_pct:
                                trail_active = True
                                trail_price = fut_high * (1 - lock_pct)
                            elif trail_active:
                                new_trail = fut_high * (1 - lock_pct)
                                if new_trail > trail_price:
                                    trail_price = new_trail

                    # Check exit conditions
                    if fut_low <= sl_price:
                        exit_price = sl_price
                        break
                    elif trail_active and fut_low <= trail_price:
                        exit_price = trail_price
                        break
                    elif fut_high >= target_price:
                        exit_price = target_price
                        break

                else:  # SHORT
                    # Check for trailing stop activation
                    if trigger_pct and lock_pct:
                        curr_profit_pct = (entry_price - fut_low) / entry_price
                        if curr_profit_pct > max_profit_pct:
                            max_profit_pct = curr_profit_pct
                            if not trail_active and curr_profit_pct >= trigger_pct:
                                trail_active = True
                                trail_price = fut_low * (1 + lock_pct)
                            elif trail_active:
                                new_trail = fut_low * (1 + lock_pct)
                                if new_trail < trail_price:
                                    trail_price = new_trail

                    # Check exit conditions
                    if fut_high >= sl_price:
                        exit_price = sl_price
                        break
                    elif trail_active and fut_high >= trail_price:
                        exit_price = trail_price
                        break
                    elif fut_low <= target_price:
                        exit_price = target_price
                        break

                # Check if we've reached end of day
                if fut_time >= end_time:
                    exit_price = fut['Close']
                    break

            # If no exit triggered, use close price
            if 'exit_price' not in locals():
                exit_price = market.iloc[j]['Close']

            # Calculate PnL
            pnl = (exit_price - entry_price) if direction == 'LONG' else (entry_price - exit_price)
            balance += pnl

            # Log trade
            trade_log.append({
                'trade_type': f'Entry {direction.lower()}',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'sl': sl_price,
                'target': target_price,
                'trail_price': trail_price if trail_active else None,
                'pnl': pnl,
                'date': date,
                'time': time,
                'exit_time': fut_time,
                'max_profit_pct': max_profit_pct * 100
            })
            equity_curve.append(balance)

            # Update reentry tracker
            if key not in reentry_tracker:
                reentry_tracker[key] = {'count': 1, 'next_entry': i + 1}
            else:
                reentry_tracker[key]['count'] += 1
                reentry_tracker[key]['next_entry'] = i + config.reentry_delay if config.reentry_delay else i + 1

    # Calculate summary statistics
    winning_trades = [t for t in trade_log if t['pnl'] > 0]
    losing_trades = [t for t in trade_log if t['pnl'] <= 0]
    
    summary = {
        'total_pnl': balance,
        'num_trades': len(trade_log),
        'win_rate': len(winning_trades) / len(trade_log) if trade_log else 0,
        'avg_win': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
        'avg_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
        'max_drawdown': min(equity_curve) if equity_curve else 0,
        'profit_factor': abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades else float('inf')
    }

    return BacktestResult(
        summary=summary,
        trade_log=trade_log,
        equity_curve=equity_curve
    )

# Save/load strategy
@app.post("/strategy/save")
def save_strategy_endpoint(name: str = Form(...), config: str = Form(...)):
    save_strategy(name, config)
    return {"status": "saved"}

@app.get("/strategy/{name}")
def get_strategy_endpoint(name: str):
    config = get_strategy(name)
    if not config:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"config": config}

@app.post("/strategy/{name}/retry", response_model=BacktestResult)
def retry_strategy(name: str):
    import json
    config_json = get_strategy(name)
    if not config_json:
        raise HTTPException(status_code=404, detail="Strategy not found")
    config = BacktestConfig.parse_raw(config_json)
    return run_backtest(config)
