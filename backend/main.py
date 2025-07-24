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

def calculate_max_consecutive(trade_log, type_):
    """Calculate maximum consecutive wins or losses"""
    if not trade_log:
        return 0
    
    max_consecutive = 0
    current_consecutive = 0
    
    for trade in trade_log:
        if type_ == 'win' and trade['pnl'] > 0:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        elif type_ == 'loss' and trade['pnl'] <= 0:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    return max_consecutive

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
    daily_pnl = {}
    reentry_tracker = {}

    # Get configuration parameters
    position_size = getattr(config, 'position_size', 100)
    slippage = getattr(config, 'slippage', 0.5)
    brokerage = getattr(config, 'brokerage', 20.0)
    tax_rate = getattr(config, 'tax_rate', 15.0) / 100
    max_loss_per_day = getattr(config, 'max_loss_per_day', 5000.0)

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

            # Apply slippage
            if direction == 'LONG':
                entry_price_with_slippage = entry_price + slippage
                exit_price_with_slippage = exit_price - slippage
            else:
                entry_price_with_slippage = entry_price - slippage
                exit_price_with_slippage = exit_price + slippage

            # Calculate gross PnL
            gross_pnl = (exit_price_with_slippage - entry_price_with_slippage) * position_size if direction == 'LONG' else (entry_price_with_slippage - exit_price_with_slippage) * position_size
            
            # Apply trading costs
            total_brokerage = brokerage * 2  # Entry + Exit
            tax_amount = max(0, gross_pnl) * tax_rate if gross_pnl > 0 else 0
            net_pnl = gross_pnl - total_brokerage - tax_amount
            
            # Check daily loss limit
            current_date = date
            if current_date not in daily_pnl:
                daily_pnl[current_date] = 0
            
            if daily_pnl[current_date] + net_pnl < -max_loss_per_day:
                continue  # Skip this trade if it exceeds daily loss limit
            
            daily_pnl[current_date] += net_pnl
            balance += net_pnl

            # Log trade with detailed information
            trade_log.append({
                'trade_type': f'Entry {direction.lower()}',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'entry_price_with_slippage': entry_price_with_slippage,
                'exit_price_with_slippage': exit_price_with_slippage,
                'sl': sl_price,
                'target': target_price,
                'trail_price': trail_price if trail_active else None,
                'gross_pnl': gross_pnl,
                'brokerage': total_brokerage,
                'tax': tax_amount,
                'pnl': net_pnl,
                'date': date,
                'time': time,
                'exit_time': fut_time,
                'max_profit_pct': max_profit_pct * 100,
                'position_size': position_size,
                'direction': direction
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
    
    # Calculate additional metrics
    total_gross_pnl = sum(t['gross_pnl'] for t in trade_log) if trade_log else 0
    total_brokerage = sum(t['brokerage'] for t in trade_log) if trade_log else 0
    total_tax = sum(t['tax'] for t in trade_log) if trade_log else 0
    
    # Calculate maximum consecutive wins/losses
    max_consecutive_wins = calculate_max_consecutive(trade_log, 'win')
    max_consecutive_losses = calculate_max_consecutive(trade_log, 'loss')
    
    # Calculate Sharpe ratio (simplified)
    if len(equity_curve) > 1:
        returns = [equity_curve[i] - equity_curve[i-1] for i in range(1, len(equity_curve))]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0
        sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
    else:
        sharpe_ratio = 0
    
    summary = {
        'total_pnl': balance,
        'total_gross_pnl': total_gross_pnl,
        'total_brokerage': total_brokerage,
        'total_tax': total_tax,
        'num_trades': len(trade_log),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': len(winning_trades) / len(trade_log) if trade_log else 0,
        'avg_win': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
        'avg_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
        'max_drawdown': min(equity_curve) if equity_curve else 0,
        'profit_factor': abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades else float('inf'),
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'sharpe_ratio': sharpe_ratio,
        'total_return_pct': (balance / 100000) * 100 if balance else 0,  # Assuming initial capital of 1 lakh
        'daily_pnl_stats': daily_pnl
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
