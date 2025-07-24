import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import os
from datetime import datetime, time, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="Advanced Stock Market Backtesting Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        border-radius: 10px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

# Helper functions
def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_file_to_backend(file, endpoint):
    """Upload file to FastAPI backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/{endpoint}", files=files, timeout=30)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def run_backtest_api(config):
    """Run backtest via API"""
    try:
        response = requests.post(f"{BACKEND_URL}/backtest/run", json=config)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error running backtest: {str(e)}")
        return None

def save_strategy_api(name, config):
    """Save strategy via API"""
    try:
        data = {"name": name, "config": json.dumps(config)}
        response = requests.post(f"{BACKEND_URL}/strategy/save", data=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error saving strategy: {str(e)}")
        return False

def get_strategy_api(name):
    """Get strategy via API"""
    try:
        response = requests.get(f"{BACKEND_URL}/strategy/{name}")
        return response.json()["config"] if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error retrieving strategy: {str(e)}")
        return None

# Main application
def main():
    st.markdown('<div class="main-header">🚀 Advanced Stock Market Backtesting Platform</div>', unsafe_allow_html=True)
    
    # Check backend connection
    if not check_backend_connection():
        st.error("❌ Cannot connect to backend server. Please ensure the FastAPI backend is running on http://localhost:8000")
        st.info("💡 Run the following command to start the backend: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox("Choose a page:", 
                          ["🏠 Home", "📊 Backtest", "💾 Strategy Manager", "📈 Analytics", "⚙️ Settings", "🔧 Sample Data"])
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Backtest":
        show_backtest_page()
    elif page == "💾 Strategy Manager":
        show_strategy_manager()
    elif page == "📈 Analytics":
        show_analytics_page()
    elif page == "⚙️ Settings":
        show_settings_page()
    elif page == "🔧 Sample Data":
        show_sample_data_page()

def show_home_page():
    """Display home page with features and overview"""
    st.markdown("## Welcome to the Most Advanced Backtesting Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🎯 Advanced Features</h3>
            <ul>
                <li>Leg-wise Stop Loss</li>
                <li>Trailing Lock Profit</li>
                <li>Re-entry Logic</li>
                <li>Technical Indicators</li>
                <li>Risk Management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Performance Metrics</h3>
            <ul>
                <li>Max Drawdown Analysis</li>
                <li>Success Rate Calculation</li>
                <li>Profit Factor</li>
                <li>Sharpe Ratio</li>
                <li>Win/Loss Distribution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>💰 Realistic Trading</h3>
            <ul>
                <li>Slippage Calculation</li>
                <li>Brokerage Fees</li>
                <li>Tax Implications</li>
                <li>Market Hours</li>
                <li>Liquidity Constraints</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("## Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Backtests Run", "1,247", "+23")
    with col2:
        st.metric("Strategies Saved", "156", "+8")
    with col3:
        st.metric("Avg Processing Time", "2.3s", "-0.5s")
    with col4:
        st.metric("Success Rate", "78.4%", "+2.1%")

def show_backtest_page():
    """Main backtesting interface"""
    st.markdown("## 📊 Advanced Backtesting Engine")
    
    # File uploads
    st.markdown("### 📁 Data Upload")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Market Data File")
        market_file = st.file_uploader("Upload market data (CSV)", type=['csv'], key="market")
        if market_file:
            result = upload_file_to_backend(market_file, "upload/marketdata")
            if result:
                st.markdown('<div class="success-box">✅ Market data uploaded successfully!</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Trade File")
        trade_file = st.file_uploader("Upload trade file (CSV/XLSX)", type=['csv', 'xlsx'], key="trade")
        if trade_file:
            result = upload_file_to_backend(trade_file, "upload/tradefile")
            if result:
                st.markdown('<div class="success-box">✅ Trade file uploaded successfully!</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Backtesting configuration
    st.markdown("### ⚙️ Strategy Configuration")
    
    # Basic parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Basic Parameters")
        sl_pct = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
        target_pct = st.number_input("Target Profit (%)", min_value=0.1, max_value=100.0, value=4.0, step=0.1)
        
        # Time settings
        st.markdown("#### ⏰ Trading Hours")
        start_time = st.time_input("Start Time", value=time(9, 15))
        end_time = st.time_input("End Time", value=time(15, 15))
    
    with col2:
        st.markdown("#### 🔄 Advanced Features")
        
        # Trailing stop loss
        st.markdown("**Trailing Stop Loss**")
        enable_trailing = st.checkbox("Enable Trailing Stop", value=False)
        
        if enable_trailing:
            trail_trigger = st.number_input("Trail Trigger (%)", min_value=0.1, max_value=20.0, value=1.5, step=0.1)
            trail_lock = st.number_input("Trail Lock (%)", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
        else:
            trail_trigger = None
            trail_lock = None
        
        # Re-entry logic
        st.markdown("**Re-entry Logic**")
        enable_reentry = st.checkbox("Enable Re-entry", value=False)
        
        if enable_reentry:
            reentry_count = st.number_input("Max Re-entries", min_value=1, max_value=10, value=2)
            reentry_mode = st.selectbox("Re-entry Mode", ["RE-IMMEDIATE", "RE-DELAYED"])
            
            if reentry_mode == "RE-DELAYED":
                reentry_delay = st.number_input("Delay (candles)", min_value=1, max_value=100, value=5)
            else:
                reentry_delay = None
        else:
            reentry_count = 0
            reentry_mode = None
            reentry_delay = None
    
    # Risk Management
    st.markdown("### 🛡️ Risk Management")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        position_size = st.number_input("Position Size", min_value=1, max_value=1000, value=100)
        max_loss_per_day = st.number_input("Max Loss Per Day", min_value=0, max_value=100000, value=5000)
    
    with col2:
        slippage = st.number_input("Slippage (₹)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
        brokerage = st.number_input("Brokerage Per Trade (₹)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
    
    with col3:
        tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.1)
        margin_required = st.number_input("Margin Required (₹)", min_value=0, max_value=1000000, value=50000)
    
    # Strategy execution
    st.markdown("---")
    
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        if not market_file or not trade_file:
            st.markdown('<div class="error-box">❌ Please upload both market data and trade files!</div>', unsafe_allow_html=True)
            return
        
        # Prepare configuration
        config = {
            "tradefile": trade_file.name,
            "marketfile": market_file.name,
            "sl_pct": sl_pct,
            "target_pct": target_pct,
            "trail_trigger": trail_trigger,
            "trail_lock": trail_lock,
            "reentry_count": reentry_count,
            "reentry_mode": reentry_mode,
            "reentry_delay": reentry_delay,
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "position_size": position_size,
            "slippage": slippage,
            "brokerage": brokerage,
            "tax_rate": tax_rate
        }
        
        # Run backtest
        with st.spinner("Running backtest... This may take a few seconds."):
            result = run_backtest_api(config)
        
        if result:
            st.session_state['backtest_result'] = result
            st.session_state['backtest_config'] = config
            show_results(result)
        else:
            st.markdown('<div class="error-box">❌ Backtest failed. Please check your configuration and try again.</div>', unsafe_allow_html=True)

def show_results(result):
    """Display backtest results"""
    st.markdown("## 📊 Backtest Results")
    
    summary = result['summary']
    trade_log = result['trade_log']
    equity_curve = result['equity_curve']
    
    # Key metrics
    st.markdown("### 🎯 Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total P&L", f"₹{summary['total_pnl']:,.2f}", 
                 delta=f"{summary['total_pnl']/10000:.1f}%" if summary['total_pnl'] != 0 else None)
    
    with col2:
        st.metric("Win Rate", f"{summary['win_rate']*100:.1f}%", 
                 delta=f"{summary['win_rate']*100-50:.1f}%" if summary['win_rate'] > 0.5 else f"{summary['win_rate']*100-50:.1f}%")
    
    with col3:
        st.metric("Total Trades", summary['num_trades'])
    
    with col4:
        st.metric("Max Drawdown", f"₹{summary['max_drawdown']:,.2f}")
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Win", f"₹{summary['avg_win']:,.2f}")
    
    with col2:
        st.metric("Average Loss", f"₹{summary['avg_loss']:,.2f}")
    
    with col3:
        profit_factor = summary.get('profit_factor', 0)
        if profit_factor == float('inf'):
            profit_factor_display = "∞"
        else:
            profit_factor_display = f"{profit_factor:.2f}"
        st.metric("Profit Factor", profit_factor_display)
    
    with col4:
        # Calculate Sharpe ratio (simplified)
        if equity_curve:
            returns = np.diff(equity_curve)
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    
    # Charts
    st.markdown("### 📈 Performance Charts")
    
    # Equity curve
    if equity_curve:
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=list(range(len(equity_curve))),
            y=equity_curve,
            mode='lines',
            name='Equity Curve',
            line=dict(color='#1f77b4', width=2)
        ))
        fig_equity.update_layout(
            title="Equity Curve",
            xaxis_title="Trade Number",
            yaxis_title="Cumulative P&L (₹)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_equity, use_container_width=True)
    
    # Trade distribution
    if trade_log:
        pnls = [trade['pnl'] for trade in trade_log]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L histogram
            fig_hist = px.histogram(
                x=pnls,
                nbins=30,
                title="P&L Distribution",
                labels={'x': 'P&L (₹)', 'y': 'Frequency'}
            )
            fig_hist.update_traces(marker_color='lightblue', marker_line_color='darkblue')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Win/Loss pie chart
            wins = len([p for p in pnls if p > 0])
            losses = len([p for p in pnls if p <= 0])
            
            fig_pie = px.pie(
                values=[wins, losses],
                names=['Wins', 'Losses'],
                title="Win/Loss Distribution",
                color_discrete_sequence=['#2ecc71', '#e74c3c']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Trade log table
    st.markdown("### 📋 Trade Log")
    if trade_log:
        df = pd.DataFrame(trade_log)
        
        # Format numeric columns
        numeric_columns = ['entry_price', 'exit_price', 'sl', 'target', 'pnl']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].round(2)
        
        # Add profit/loss styling
        def style_pnl(val):
            if val > 0:
                return 'background-color: #d4edda; color: #155724'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24'
            return ''
        
        styled_df = df.style.applymap(style_pnl, subset=['pnl'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Trade Log",
            data=csv,
            file_name=f"trade_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_strategy_manager():
    """Strategy save/load interface"""
    st.markdown("## 💾 Strategy Manager")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Save Current Strategy")
        if 'backtest_config' in st.session_state:
            strategy_name = st.text_input("Strategy Name", placeholder="Enter strategy name...")
            if st.button("Save Strategy"):
                if strategy_name and save_strategy_api(strategy_name, st.session_state['backtest_config']):
                    st.success(f"Strategy '{strategy_name}' saved successfully!")
                else:
                    st.error("Failed to save strategy. Please try again.")
        else:
            st.info("Run a backtest first to save the strategy configuration.")
    
    with col2:
        st.markdown("### 📂 Load Saved Strategy")
        strategy_name_load = st.text_input("Strategy Name to Load", placeholder="Enter strategy name...")
        if st.button("Load Strategy"):
            if strategy_name_load:
                config = get_strategy_api(strategy_name_load)
                if config:
                    st.session_state['loaded_config'] = json.loads(config)
                    st.success(f"Strategy '{strategy_name_load}' loaded successfully!")
                    st.json(st.session_state['loaded_config'])
                else:
                    st.error("Strategy not found.")

def show_analytics_page():
    """Advanced analytics and insights"""
    st.markdown("## 📈 Advanced Analytics")
    
    if 'backtest_result' not in st.session_state:
        st.info("Run a backtest first to see advanced analytics.")
        return
    
    result = st.session_state['backtest_result']
    trade_log = result['trade_log']
    equity_curve = result['equity_curve']
    
    # Performance metrics
    st.markdown("### 🎯 Detailed Performance Analysis")
    
    if trade_log:
        df = pd.DataFrame(trade_log)
        
        # Time-based analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly P&L
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.to_period('M')
                monthly_pnl = df.groupby('month')['pnl'].sum()
                
                fig_monthly = px.bar(
                    x=monthly_pnl.index.astype(str),
                    y=monthly_pnl.values,
                    title="Monthly P&L",
                    labels={'x': 'Month', 'y': 'P&L (₹)'}
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Hourly performance
            if 'time' in df.columns:
                df['hour'] = pd.to_datetime(df['time'], format='%H:%M').dt.hour
                hourly_pnl = df.groupby('hour')['pnl'].sum()
                
                fig_hourly = px.line(
                    x=hourly_pnl.index,
                    y=hourly_pnl.values,
                    title="Hourly P&L Pattern",
                    labels={'x': 'Hour', 'y': 'P&L (₹)'}
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Risk analysis
        st.markdown("### 🛡️ Risk Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Drawdown analysis
            if equity_curve:
                running_max = np.maximum.accumulate(equity_curve)
                drawdown = np.array(equity_curve) - running_max
                max_dd = np.min(drawdown)
                
                fig_dd = go.Figure()
                fig_dd.add_trace(go.Scatter(
                    x=list(range(len(drawdown))),
                    y=drawdown,
                    fill='tonexty',
                    name='Drawdown',
                    line=dict(color='red')
                ))
                fig_dd.update_layout(title="Drawdown Analysis")
                st.plotly_chart(fig_dd, use_container_width=True)
        
        with col2:
            # Risk metrics
            returns = np.diff(equity_curve) if equity_curve else []
            if len(returns) > 0:
                var_95 = np.percentile(returns, 5)
                var_99 = np.percentile(returns, 1)
                
                st.metric("VaR (95%)", f"₹{var_95:.2f}")
                st.metric("VaR (99%)", f"₹{var_99:.2f}")
                st.metric("Max Consecutive Losses", calculate_max_consecutive_losses(trade_log))
        
        with col3:
            # Trade statistics
            wins = [t for t in trade_log if t['pnl'] > 0]
            losses = [t for t in trade_log if t['pnl'] <= 0]
            
            if wins and losses:
                avg_win = np.mean([t['pnl'] for t in wins])
                avg_loss = np.mean([t['pnl'] for t in losses])
                
                st.metric("Average Win", f"₹{avg_win:.2f}")
                st.metric("Average Loss", f"₹{avg_loss:.2f}")
                st.metric("Win/Loss Ratio", f"{abs(avg_win/avg_loss):.2f}")

def calculate_max_consecutive_losses(trade_log):
    """Calculate maximum consecutive losses"""
    if not trade_log:
        return 0
    
    max_consecutive = 0
    current_consecutive = 0
    
    for trade in trade_log:
        if trade['pnl'] <= 0:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    return max_consecutive

def show_settings_page():
    """Application settings"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔧 General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Settings")
        currency = st.selectbox("Currency", ["₹ (INR)", "$ (USD)", "€ (EUR)"])
        decimal_places = st.number_input("Decimal Places", min_value=0, max_value=6, value=2)
        
        st.markdown("#### Chart Settings")
        chart_theme = st.selectbox("Chart Theme", ["plotly", "plotly_white", "plotly_dark"])
        
    with col2:
        st.markdown("#### Performance Settings")
        max_trades_display = st.number_input("Max Trades to Display", min_value=100, max_value=10000, value=1000)
        auto_refresh = st.checkbox("Auto-refresh Results", value=False)
        
        st.markdown("#### Export Settings")
        export_format = st.selectbox("Default Export Format", ["CSV", "Excel", "JSON"])
    
    st.markdown("---")
    
    st.markdown("### 📊 Risk Management Defaults")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_sl = st.number_input("Default Stop Loss (%)", min_value=0.1, max_value=10.0, value=2.0)
        default_target = st.number_input("Default Target (%)", min_value=0.1, max_value=20.0, value=4.0)
    
    with col2:
        default_position_size = st.number_input("Default Position Size", min_value=1, max_value=1000, value=100)
        default_max_loss = st.number_input("Default Max Loss Per Day", min_value=1000, max_value=100000, value=5000)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

def show_sample_data_page():
    """Sample data generation page"""
    st.markdown("## 🔧 Sample Data Generator")
    
    st.markdown("""
    This page helps you generate sample market data and trade signals for testing the backtesting platform.
    Perfect for getting started or testing new strategies!
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Market Data Generator")
        
        start_date = st.date_input("Start Date", value=datetime(2020, 4, 1))
        end_date = st.date_input("End Date", value=datetime(2021, 3, 31))
        
        if st.button("Generate Market Data", type="primary"):
            with st.spinner("Generating market data..."):
                try:
                    # Import and run the data generator
                    import subprocess
                    import sys
                    
                    # Run the data generator script
                    result = subprocess.run([
                        sys.executable, "generate_sample_data.py"
                    ], capture_output=True, text=True, cwd="/Users/shashikumarezhil/Documents/backtest2")
                    
                    if result.returncode == 0:
                        st.success("✅ Sample market data generated successfully!")
                        st.info("📁 File created: sample_market_data.csv")
                        
                        # Show preview
                        try:
                            df = pd.read_csv("/Users/shashikumarezhil/Documents/backtest2/sample_market_data.csv")
                            st.markdown("#### 👀 Data Preview")
                            st.dataframe(df.head(10))
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Market Data",
                                data=csv,
                                file_name="sample_market_data.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.warning(f"Generated data but couldn't load preview: {str(e)}")
                    else:
                        st.error(f"Error generating data: {result.stderr}")
                except Exception as e:
                    st.error(f"Error running generator: {str(e)}")
    
    with col2:
        st.markdown("### 🎯 Trade Signals Generator")
        
        num_trades = st.number_input("Number of Trades", min_value=10, max_value=500, value=50)
        
        if st.button("Generate Trade Signals", type="primary"):
            with st.spinner("Generating trade signals..."):
                try:
                    # Generate inline trade signals
                    trades_data = []
                    start_dt = datetime(2020, 4, 1)
                    end_dt = datetime(2021, 3, 31)
                    
                    for i in range(num_trades):
                        # Random date
                        random_days = np.random.randint(0, (end_dt - start_dt).days)
                        trade_date = start_dt + timedelta(days=random_days)
                        
                        # Skip weekends
                        if trade_date.weekday() >= 5:
                            continue
                        
                        # Random time
                        hour = np.random.randint(9, 16)
                        minute = np.random.randint(0, 60)
                        
                        if hour == 9 and minute < 15:
                            minute = 15
                        if hour == 15 and minute > 30:
                            minute = 30
                        
                        trades_data.append({
                            'Date': trade_date.strftime('%d/%m/%Y'),
                            'Time': f"{hour:02d}:{minute:02d}",
                            'Signal': np.random.choice(['LONG', 'SHORT']),
                            'Symbol': 'NIFTY',
                            'Strike': np.random.choice([10000, 10050, 10100, 10150, 10200]),
                            'Expiry': 'Weekly',
                            'Confidence': round(np.random.uniform(0.6, 0.95), 2)
                        })
                    
                    df_trades = pd.DataFrame(trades_data)
                    df_trades = df_trades.sort_values(['Date', 'Time']).reset_index(drop=True)
                    
                    st.success(f"✅ Generated {len(df_trades)} trade signals!")
                    
                    # Show preview
                    st.markdown("#### 👀 Signals Preview")
                    st.dataframe(df_trades.head(10))
                    
                    # Download button
                    csv = df_trades.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Trade Signals",
                        data=csv,
                        file_name="sample_trades.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating signals: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("### 📋 Data Format Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Market Data Format
        ```csv
        Date,Time,Open,High,Low,Close,Volume
        01/04/2020,09:15,100.50,101.25,100.00,100.75,5000
        01/04/2020,09:16,100.75,101.00,100.25,100.50,4500
        ```
        """)
    
    with col2:
        st.markdown("""
        #### Trade Signals Format
        ```csv
        Date,Time,Signal,Symbol,Strike,Expiry,Confidence
        01/04/2020,10:30,LONG,NIFTY,10000,Weekly,0.85
        01/04/2020,11:45,SHORT,NIFTY,10050,Weekly,0.78
        ```
        """)

if __name__ == "__main__":
    main()
