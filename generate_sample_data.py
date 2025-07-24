import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_market_data(start_date="01/04/2020", end_date="31/03/2021", filename="sample_market_data.csv"):
    """
    Generate sample market data for testing the backtesting platform
    """
    
    # Convert dates
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y")
    
    # Generate date range (only trading days - Monday to Friday)
    dates = []
    current_date = start
    while current_date <= end:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Market hours (9:15 AM to 3:30 PM, every minute)
    times = []
    start_time = 9 * 60 + 15  # 9:15 AM in minutes
    end_time = 15 * 60 + 30   # 3:30 PM in minutes
    
    for minute in range(start_time, end_time + 1):
        hour = minute // 60
        min_val = minute % 60
        times.append(f"{hour:02d}:{min_val:02d}")
    
    # Generate market data
    data = []
    base_price = 10000  # Starting price
    
    for date in dates:
        daily_volatility = random.uniform(0.5, 3.0)  # Daily volatility %
        daily_trend = random.uniform(-1.0, 1.0)     # Daily trend %
        
        prev_close = base_price
        
        for time_str in times:
            # Generate OHLC with realistic relationships
            price_change = random.gauss(daily_trend/100, daily_volatility/100) * prev_close
            
            open_price = prev_close + random.gauss(0, 0.001) * prev_close
            close_price = open_price + price_change
            
            # High and Low should respect OHLC relationships
            high_price = max(open_price, close_price) + random.uniform(0, 0.005) * prev_close
            low_price = min(open_price, close_price) - random.uniform(0, 0.005) * prev_close
            
            data.append({
                'Date': date.strftime('%d/%m/%Y'),
                'Time': time_str,
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': random.randint(1000, 10000)
            })
            
            prev_close = close_price
        
        # Update base price for next day
        base_price = prev_close
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Generated {len(df)} market data points in {filename}")
    return df

def generate_sample_trades(num_trades=50, filename="sample_trades.csv"):
    """
    Generate sample trade signals for testing
    """
    
    # Generate random trade dates
    start_date = datetime(2020, 4, 1)
    end_date = datetime(2021, 3, 31)
    
    trades = []
    
    for i in range(num_trades):
        # Random date between start and end
        random_days = random.randint(0, (end_date - start_date).days)
        trade_date = start_date + timedelta(days=random_days)
        
        # Skip weekends
        if trade_date.weekday() >= 5:
            continue
        
        # Random time during market hours
        hour = random.randint(9, 15)
        minute = random.randint(0, 59)
        
        # Ensure valid market hours
        if hour == 9 and minute < 15:
            minute = 15
        if hour == 15 and minute > 30:
            minute = 30
        
        trades.append({
            'Date': trade_date.strftime('%d/%m/%Y'),
            'Time': f"{hour:02d}:{minute:02d}",
            'Signal': random.choice(['LONG', 'SHORT']),
            'Symbol': 'NIFTY',
            'Strike': random.choice([10000, 10050, 10100, 10150, 10200]),
            'Expiry': 'Weekly',
            'Confidence': round(random.uniform(0.6, 0.95), 2)
        })
    
    # Create DataFrame and save
    df = pd.DataFrame(trades)
    df = df.sort_values(['Date', 'Time']).reset_index(drop=True)
    df.to_csv(filename, index=False)
    print(f"Generated {len(df)} trade signals in {filename}")
    return df

if __name__ == "__main__":
    print("🔧 Generating sample data for backtesting platform...")
    
    # Generate market data
    market_df = generate_sample_market_data()
    
    # Generate trade signals
    trades_df = generate_sample_trades()
    
    print("\n✅ Sample data generation completed!")
    print("📁 Files created:")
    print("   - sample_market_data.csv (Market OHLC data)")
    print("   - sample_trades.csv (Trade signals)")
    print("\n📊 You can now upload these files to test the backtesting platform!")
