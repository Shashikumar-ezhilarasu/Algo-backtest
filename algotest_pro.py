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
    page_title="AlgoBacktest Pro - Advanced Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Enhanced version
st.markdown("""
<style>
    /* Global Styles */
    .main > div {
        padding: 0 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional Header */
    .platform-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #9b59b6 100%);
        padding: 1.5rem 2rem;
        color: white;
        margin: -1rem -1rem 0 -1rem;
        position: relative;
        overflow: hidden;
    }
    
    .platform-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
        opacity: 0.1;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
    }
    
    .platform-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .platform-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    .header-stats {
        position: absolute;
        right: 2rem;
        top: 50%;
        transform: translateY(-50%);
        text-align: right;
    }
    
    .header-stat {
        display: block;
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 0.25rem;
    }
    
    /* Navigation Bar */
    .nav-container {
        background: #34495e;
        padding: 0;
        margin: 0 -1rem 2rem -1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .nav-item {
        display: inline-block;
        padding: 1rem 2rem;
        color: #ecf0f1;
        cursor: pointer;
        transition: all 0.3s ease;
        border-bottom: 3px solid transparent;
        font-weight: 500;
        position: relative;
    }
    
    .nav-item:hover {
        background: #2c3e50;
        border-bottom-color: #3498db;
    }
    
    .nav-item.active {
        background: #2c3e50;
        border-bottom-color: #e74c3c;
        color: white;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #3498db, #e74c3c, #f39c12, #27ae60);
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Metric Cards */
    .metric-card-pro {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-card-pro::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #3498db, #9b59b6);
    }
    
    .metric-card-pro:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    }
    
    .metric-value-pro {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #2c3e50, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label-pro {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-positive {
        color: #27ae60 !important;
        background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    .metric-negative {
        color: #e74c3c !important;
        background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* Section Headers */
    .section-header-pro {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #3498db, #9b59b6) 1;
        position: relative;
    }
    
    .section-header-pro::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 50px;
        height: 3px;
        background: #e74c3c;
    }
    
    /* Feature Cards */
    .feature-card-pro {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card-pro::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(52, 152, 219, 0.1), transparent);
        transform: rotate(-45deg);
        transition: all 0.6s ease;
        opacity: 0;
    }
    
    .feature-card-pro:hover::before {
        opacity: 1;
        transform: rotate(-45deg) translate(50%, 50%);
    }
    
    .feature-card-pro:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        border-color: #3498db;
    }
    
    .feature-icon-pro {
        font-size: 4rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #3498db, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-title-pro {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .feature-desc-pro {
        color: #7f8c8d;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Buttons */
    .btn-pro {
        background: linear-gradient(135deg, #3498db 0%, #9b59b6 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .btn-pro:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
    }
    
    .btn-success {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    /* Status Badges */
    .status-badge-pro {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .status-active {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
    }
    
    .status-paused {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
    }
    
    .status-stopped {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
    }
    
    /* Strategy Builder */
    .strategy-section {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .strategy-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    /* Live indicators */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    .live-indicator.green {
        background: #27ae60;
    }
    
    .live-indicator.red {
        background: #e74c3c;
    }
    
    .live-indicator.yellow {
        background: #f39c12;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(52, 152, 219, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(52, 152, 219, 0); }
        100% { box-shadow: 0 0 0 0 rgba(52, 152, 219, 0); }
    }
    
    /* Tables */
    .dataframe {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #34495e, #2c3e50);
        color: white;
        font-weight: 600;
        padding: 1rem;
    }
    
    .dataframe td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f8f9fa;
    }
    
    .dataframe tr:hover {
        background: #f8f9fa;
    }
    
    /* Charts container */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .platform-title {
            font-size: 2rem;
        }
        
        .header-stats {
            position: relative;
            right: auto;
            top: auto;
            transform: none;
            text-align: left;
            margin-top: 1rem;
        }
        
        .nav-item {
            display: block;
            padding: 0.75rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'overview'
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None
if 'live_data' not in st.session_state:
    st.session_state.live_data = {
        'total_pnl': 124750,
        'active_strategies': 3,
        'total_trades': 1247,
        'win_rate': 78.4
    }

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
        response = requests.post(f"{BACKEND_URL}/backtest/run", json=config, timeout=60)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error running backtest: {str(e)}")
        return None

def create_professional_header():
    """Create the main header"""
    live_data = st.session_state.live_data
    
    st.markdown(f"""
    <div class="platform-header">
        <div class="header-content">
            <div class="platform-title">AlgoBacktest Pro</div>
            <div class="platform-subtitle">Professional Stock Market Backtesting & Analytics Platform</div>
        </div>
        <div class="header-stats">
            <span class="header-stat"><span class="live-indicator green"></span>Live P&L: ₹{live_data['total_pnl']:,}</span>
            <span class="header-stat"><span class="live-indicator yellow"></span>Active Strategies: {live_data['active_strategies']}</span>
            <span class="header-stat"><span class="live-indicator green"></span>Win Rate: {live_data['win_rate']}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_navigation():
    """Create professional navigation"""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    pages = [
        ("📊", "Dashboard", "overview"),
        ("⚙️", "Strategy Builder", "strategy"),
        ("🚀", "Backtest Engine", "backtest"),
        ("📈", "Analytics", "results"),
        ("💼", "Portfolio", "portfolio"),
        ("⚡", "Live Trading", "live")
    ]
    
    cols = [col1, col2, col3, col4, col5, col6]
    
    for i, (icon, label, page_key) in enumerate(pages):
        with cols[i]:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

def show_dashboard():
    """Professional dashboard overview"""
    st.markdown('<div class="section-header-pro">📊 Trading Dashboard</div>', unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics_data = [
        ("₹1,24,750", "Portfolio Value", "positive"),
        ("78.4%", "Success Rate", "positive"),
        ("1,247", "Total Trades", "neutral"),
        ("-₹8,450", "Max Drawdown", "negative"),
        ("2.34", "Sharpe Ratio", "positive")
    ]
    
    cols = [col1, col2, col3, col4, col5]
    
    for i, (value, label, status) in enumerate(metrics_data):
        with cols[i]:
            status_class = f"metric-{status}" if status != "neutral" else ""
            st.markdown(f"""
            <div class="metric-card-pro">
                <div class="metric-value-pro {status_class}">{value}</div>
                <div class="metric-label-pro">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts section
    st.markdown('<div class="section-header-pro">📈 Performance Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sample equity curve
        dates = pd.date_range(start='2024-01-01', end='2024-07-24', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        equity = 100000 * (1 + returns).cumprod()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#3498db', width=3),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        fig.update_layout(
            title="Portfolio Equity Curve",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(gridcolor='#f0f0f0'),
            yaxis=dict(gridcolor='#f0f0f0')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance breakdown
        st.markdown("""
        <div class="dashboard-card">
            <h4>🎯 Performance Breakdown</h4>
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                    <span>Winning Trades:</span>
                    <span style="color: #27ae60; font-weight: bold;">978</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                    <span>Losing Trades:</span>
                    <span style="color: #e74c3c; font-weight: bold;">269</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                    <span>Avg Win:</span>
                    <span style="color: #27ae60; font-weight: bold;">₹1,245</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                    <span>Avg Loss:</span>
                    <span style="color: #e74c3c; font-weight: bold;">₹-842</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                    <span>Profit Factor:</span>
                    <span style="color: #3498db; font-weight: bold;">2.47</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown('<div class="section-header-pro">🚀 Platform Features</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("⚡", "Lightning Fast", "Process years of data in seconds"),
        ("🎯", "Precision Accurate", "Realistic costs & slippage"),
        ("📊", "Advanced Analytics", "Comprehensive metrics"),
        ("🔒", "Risk Management", "Built-in safety controls")
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="feature-card-pro">
                <div class="feature-icon-pro">{icon}</div>
                <div class="feature-title-pro">{title}</div>
                <div class="feature-desc-pro">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<div class="section-header-pro">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 New Backtest", use_container_width=True, type="primary"):
            st.session_state.current_page = 'strategy'
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = 'results'
            st.rerun()
    
    with col3:
        if st.button("💼 Manage Portfolio", use_container_width=True):
            st.session_state.current_page = 'portfolio'
            st.rerun()

def show_strategy_builder():
    """Enhanced strategy builder"""
    st.markdown('<div class="section-header-pro">⚙️ Advanced Strategy Builder</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown("""
    <div class="strategy-section">
        <div class="strategy-title">📁 Data Upload</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        market_file = st.file_uploader(
            "📈 Market Data (CSV)",
            type=['csv'],
            help="Upload OHLC market data with Date, Time, Open, High, Low, Close columns"
        )
        
        if market_file:
            st.markdown('<span class="status-badge-pro status-active">✓ Market Data Loaded</span>', unsafe_allow_html=True)
            
            # Show preview
            try:
                df_preview = pd.read_csv(market_file).head(3)
                st.caption("Preview:")
                st.dataframe(df_preview, use_container_width=True)
            except:
                st.caption("File loaded successfully")
    
    with col2:
        trade_file = st.file_uploader(
            "🎯 Trade Signals (CSV/XLSX)",
            type=['csv', 'xlsx'],
            help="Upload your trading signals with Date, Time, Signal columns"
        )
        
        if trade_file:
            st.markdown('<span class="status-badge-pro status-active">✓ Signals Loaded</span>', unsafe_allow_html=True)
            
            # Show preview
            try:
                if trade_file.name.endswith('.xlsx'):
                    df_preview = pd.read_excel(trade_file).head(3)
                else:
                    df_preview = pd.read_csv(trade_file).head(3)
                st.caption("Preview:")
                st.dataframe(df_preview, use_container_width=True)
            except:
                st.caption("File loaded successfully")
    
    # Strategy parameters
    st.markdown("""
    <div class="strategy-section">
        <div class="strategy-title">⚙️ Strategy Configuration</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Risk Management**")
        sl_pct = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
        target_pct = st.number_input("Target Profit (%)", min_value=0.1, max_value=100.0, value=4.0, step=0.1)
        max_loss = st.number_input("Daily Loss Limit (₹)", min_value=0, max_value=100000, value=5000, step=500)
    
    with col2:
        st.markdown("**📊 Position Management**")
        position_size = st.number_input("Position Size", min_value=1, max_value=1000, value=100, step=10)
        capital = st.number_input("Capital (₹)", min_value=10000, max_value=10000000, value=100000, step=10000)
        leverage = st.selectbox("Leverage", [1, 2, 3, 4, 5], index=0)
    
    with col3:
        st.markdown("**💰 Trading Costs**")
        slippage = st.number_input("Slippage (₹)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
        brokerage = st.number_input("Brokerage (₹)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.5)
    
    # Advanced features
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔄 Trailing Stop Loss**")
        enable_trailing = st.checkbox("Enable Trailing SL", value=False)
        if enable_trailing:
            trail_trigger = st.number_input("Trigger (%)", min_value=0.1, max_value=20.0, value=1.5, step=0.1, key="trail_trigger")
            trail_lock = st.number_input("Lock (%)", min_value=0.1, max_value=10.0, value=0.5, step=0.1, key="trail_lock")
        else:
            trail_trigger = None
            trail_lock = None
    
    with col2:
        st.markdown("**↩️ Re-entry Logic**")
        enable_reentry = st.checkbox("Enable Re-entry", value=False)
        if enable_reentry:
            reentry_count = st.number_input("Max Re-entries", min_value=1, max_value=10, value=2, key="reentry_count")
            reentry_mode = st.selectbox("Re-entry Mode", ["RE-IMMEDIATE", "RE-DELAYED"], key="reentry_mode")
            if reentry_mode == "RE-DELAYED":
                reentry_delay = st.number_input("Delay (candles)", min_value=1, max_value=100, value=5, key="reentry_delay")
            else:
                reentry_delay = None
        else:
            reentry_count = 0
            reentry_mode = None
            reentry_delay = None
    
    with col3:
        st.markdown("**⏰ Trading Hours**")
        start_time = st.time_input("Market Open", value=time(9, 15))
        end_time = st.time_input("Market Close", value=time(15, 15))
        
        st.markdown("**📊 Technical Indicators**")
        use_ema = st.checkbox("Use EMA", value=True)
        use_rsi = st.checkbox("Use RSI", value=True)
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save Strategy", use_container_width=True):
            st.success("✅ Strategy saved to portfolio!")
    
    with col2:
        if st.button("📊 Preview", use_container_width=True):
            # Show strategy preview
            st.info("📋 Strategy preview will be displayed here")
    
    with col3:
        if st.button("🧪 Quick Test", use_container_width=True):
            st.info("⚡ Running quick validation...")
    
    with col4:
        if st.button("🚀 Run Full Backtest", use_container_width=True, type="primary"):
            if market_file and trade_file:
                with st.spinner("🔄 Executing backtest..."):
                    # Upload files
                    market_upload = upload_file_to_backend(market_file, "upload/marketdata")
                    trade_upload = upload_file_to_backend(trade_file, "upload/tradefile")
                    
                    if market_upload and trade_upload:
                        # Prepare config
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
                            "position_size": position_size,
                            "slippage": slippage,
                            "brokerage": brokerage,
                            "tax_rate": tax_rate,
                            "max_loss_per_day": max_loss,
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": end_time.strftime("%H:%M")
                        }
                        
                        # Run backtest
                        result = run_backtest_api(config)
                        
                        if result:
                            st.session_state.backtest_results = result
                            st.session_state.current_page = 'results'
                            st.success("✅ Backtest completed! Redirecting to results...")
                            st.rerun()
                        else:
                            st.error("❌ Backtest execution failed!")
                    else:
                        st.error("❌ File upload failed!")
            else:
                st.error("❌ Please upload both market data and trade signals!")

def show_results_page():
    """Professional results display"""
    if not st.session_state.backtest_results:
        st.markdown('<div class="section-header-pro">📈 Analytics Dashboard</div>', unsafe_allow_html=True)
        st.info("🔍 No backtest results available. Run a backtest to see detailed analytics here.")
        return
    
    result = st.session_state.backtest_results
    summary = result['summary']
    trade_log = result['trade_log']
    equity_curve = result['equity_curve']
    
    st.markdown('<div class="section-header-pro">📈 Backtest Results & Analytics</div>', unsafe_allow_html=True)
    
    # Key performance indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    performance_metrics = [
        (f"₹{summary['total_pnl']:,.0f}", "Total P&L", "positive" if summary['total_pnl'] > 0 else "negative"),
        (f"{summary['win_rate']*100:.1f}%", "Win Rate", "positive" if summary['win_rate'] > 0.6 else "negative"),
        (f"{summary['num_trades']}", "Total Trades", "neutral"),
        (f"₹{summary['max_drawdown']:,.0f}", "Max Drawdown", "negative"),
        (f"{summary.get('profit_factor', 0):.2f}" if summary.get('profit_factor') != float('inf') else "∞", "Profit Factor", "positive")
    ]
    
    cols = [col1, col2, col3, col4, col5]
    
    for i, (value, label, status) in enumerate(performance_metrics):
        with cols[i]:
            status_class = f"metric-{status}" if status != "neutral" else ""
            st.markdown(f"""
            <div class="metric-card-pro">
                <div class="metric-value-pro {status_class}">{value}</div>
                <div class="metric-label-pro">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Advanced analytics
    st.markdown('<div class="section-header-pro">📊 Advanced Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Equity curve with enhanced styling
        if equity_curve:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Portfolio Equity Curve', 'Drawdown Analysis'),
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3]
            )
            
            # Equity curve
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(equity_curve))),
                    y=equity_curve,
                    mode='lines',
                    name='Equity',
                    line=dict(color='#3498db', width=3),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            # Drawdown calculation
            running_max = np.maximum.accumulate(equity_curve)
            drawdown = np.array(equity_curve) - running_max
            
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(drawdown))),
                    y=drawdown,
                    mode='lines',
                    name='Drawdown',
                    line=dict(color='#e74c3c', width=2),
                    fill='tonexty',
                    fillcolor='rgba(231, 76, 60, 0.3)'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_xaxes(gridcolor='#f0f0f0')
            fig.update_yaxes(gridcolor='#f0f0f0')
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance statistics
        st.markdown("""
        <div class="dashboard-card">
            <h4>📊 Performance Statistics</h4>
        </div>
        """, unsafe_allow_html=True)
        
        stats = [
            ("Average Win", f"₹{summary.get('avg_win', 0):,.2f}", "positive"),
            ("Average Loss", f"₹{summary.get('avg_loss', 0):,.2f}", "negative"),
            ("Winning Trades", summary.get('winning_trades', 0), "neutral"),
            ("Losing Trades", summary.get('losing_trades', 0), "neutral"),
            ("Sharpe Ratio", f"{summary.get('sharpe_ratio', 0):.2f}", "positive"),
            ("Max Consecutive Wins", summary.get('max_consecutive_wins', 0), "positive"),
            ("Max Consecutive Losses", summary.get('max_consecutive_losses', 0), "negative"),
            ("Total Return %", f"{summary.get('total_return_pct', 0):.2f}%", "positive" if summary.get('total_return_pct', 0) > 0 else "negative")
        ]
        
        for label, value, status in stats:
            color = "#27ae60" if status == "positive" else "#e74c3c" if status == "negative" else "#34495e"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">
                <span>{label}:</span>
                <span style="color: {color}; font-weight: bold;">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Trade distribution analysis
    st.markdown('<div class="section-header-pro">🔍 Trade Analysis</div>', unsafe_allow_html=True)
    
    if trade_log:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # P&L histogram
            pnls = [trade['pnl'] for trade in trade_log]
            
            fig_hist = px.histogram(
                x=pnls,
                nbins=30,
                title="P&L Distribution",
                labels={'x': 'P&L (₹)', 'y': 'Frequency'},
                color_discrete_sequence=['#3498db']
            )
            
            fig_hist.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=300
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Monthly performance (if date data available)
            try:
                df = pd.DataFrame(trade_log)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                    df['month'] = df['date'].dt.to_period('M')
                    monthly_pnl = df.groupby('month')['pnl'].sum().reset_index()
                    monthly_pnl['month'] = monthly_pnl['month'].astype(str)
                    
                    fig_monthly = px.bar(
                        monthly_pnl,
                        x='month',
                        y='pnl',
                        title="Monthly P&L",
                        color='pnl',
                        color_continuous_scale=['#e74c3c', '#3498db', '#27ae60']
                    )
                    
                    fig_monthly.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=300,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_monthly, use_container_width=True)
                else:
                    st.info("Monthly analysis requires date information")
            except:
                st.info("Unable to generate monthly analysis")
        
        with col3:
            # Win/Loss pie chart
            wins = len([t for t in trade_log if t['pnl'] > 0])
            losses = len([t for t in trade_log if t['pnl'] <= 0])
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Winning Trades', 'Losing Trades'],
                values=[wins, losses],
                marker_colors=['#27ae60', '#e74c3c'],
                hole=0.4
            )])
            
            fig_pie.update_layout(
                title="Trade Outcome Distribution",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed trade log
    st.markdown('<div class="section-header-pro">📋 Trade Log</div>', unsafe_allow_html=True)
    
    if trade_log:
        df = pd.DataFrame(trade_log)
        
        # Format for display
        display_columns = ['date', 'time', 'direction', 'entry_price', 'exit_price', 'pnl']
        if all(col in df.columns for col in display_columns):
            df_display = df[display_columns].copy()
            df_display.columns = ['Date', 'Time', 'Direction', 'Entry Price', 'Exit Price', 'P&L']
            
            # Add styling
            def highlight_pnl(val):
                if val > 0:
                    return 'background-color: #d4edda; color: #155724'
                elif val < 0:
                    return 'background-color: #f8d7da; color: #721c24'
                return ''
            
            styled_df = df_display.style.applymap(highlight_pnl, subset=['P&L'])
            st.dataframe(styled_df, use_container_width=True, height=400)
        else:
            st.dataframe(df, use_container_width=True, height=400)
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # JSON export
            json_data = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            if st.button("📧 Email Report", use_container_width=True):
                st.info("📨 Email functionality coming soon!")

def show_portfolio_page():
    """Portfolio management interface"""
    st.markdown('<div class="section-header-pro">💼 Strategy Portfolio</div>', unsafe_allow_html=True)
    
    # Portfolio overview
    col1, col2, col3, col4 = st.columns(4)
    
    portfolio_metrics = [
        ("5", "Active Strategies", "positive"),
        ("₹2,45,750", "Total Portfolio Value", "positive"),
        ("73.2%", "Average Win Rate", "positive"),
        ("2.1", "Average Sharpe Ratio", "positive")
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, (value, label, status) in enumerate(portfolio_metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card-pro">
                <div class="metric-value-pro metric-{status}">{value}</div>
                <div class="metric-label-pro">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Strategy list
    st.markdown('<div class="section-header-pro">📊 Strategy Performance</div>', unsafe_allow_html=True)
    
    strategies = [
        {
            "name": "Momentum Breakout Pro",
            "status": "Active",
            "pnl": 75650,
            "win_rate": 82.3,
            "trades": 234,
            "sharpe": 2.45,
            "max_dd": -5240,
            "created": "2024-01-15",
            "last_trade": "2024-07-24 14:30"
        },
        {
            "name": "Mean Reversion Alpha",
            "status": "Active",
            "pnl": 45200,
            "win_rate": 68.7,
            "trades": 156,
            "sharpe": 1.89,
            "max_dd": -8450,
            "created": "2024-02-03",
            "last_trade": "2024-07-24 11:15"
        },
        {
            "name": "RSI Oversold Scanner",
            "status": "Paused",
            "pnl": -12400,
            "win_rate": 45.2,
            "trades": 89,
            "sharpe": -0.34,
            "max_dd": -15600,
            "created": "2024-03-10",
            "last_trade": "2024-07-20 16:00"
        },
        {
            "name": "Bollinger Band Squeeze",
            "status": "Active",
            "pnl": 38950,
            "win_rate": 71.4,
            "trades": 198,
            "sharpe": 2.12,
            "max_dd": -6750,
            "created": "2024-01-28",
            "last_trade": "2024-07-24 15:45"
        },
        {
            "name": "MACD Divergence",
            "status": "Testing",
            "pnl": 8450,
            "win_rate": 58.3,
            "trades": 24,
            "sharpe": 1.23,
            "max_dd": -2100,
            "created": "2024-07-15",
            "last_trade": "2024-07-24 12:30"
        }
    ]
    
    for strategy in strategies:
        # Strategy card
        st.markdown(f"""
        <div class="dashboard-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0;">{strategy['name']}</h4>
                <span class="status-badge-pro status-{strategy['status'].lower()}">{strategy['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Strategy metrics
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        metrics = [
            ("P&L", f"₹{strategy['pnl']:,}", "positive" if strategy['pnl'] > 0 else "negative"),
            ("Win Rate", f"{strategy['win_rate']}%", "positive" if strategy['win_rate'] > 60 else "negative"),
            ("Trades", strategy['trades'], "neutral"),
            ("Sharpe", f"{strategy['sharpe']:.2f}", "positive" if strategy['sharpe'] > 1 else "negative"),
            ("Max DD", f"₹{strategy['max_dd']:,}", "negative"),
            ("Created", strategy['created'], "neutral"),
            ("Last Trade", strategy['last_trade'], "neutral")
        ]
        
        cols = [col1, col2, col3, col4, col5, col6, col7]
        
        for i, (label, value, status) in enumerate(metrics):
            with cols[i]:
                color = "#27ae60" if status == "positive" else "#e74c3c" if status == "negative" else "#34495e"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.25rem;">{label}</div>
                    <div style="font-weight: bold; color: {color};">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📊 View", key=f"view_{strategy['name']}", use_container_width=True):
                st.info(f"📋 Viewing details for {strategy['name']}")
        
        with col2:
            if st.button("⚙️ Edit", key=f"edit_{strategy['name']}", use_container_width=True):
                st.info(f"✏️ Editing {strategy['name']}")
        
        with col3:
            action_label = "▶️ Start" if strategy['status'] == 'Paused' else "⏸️ Pause"
            if st.button(action_label, key=f"toggle_{strategy['name']}", use_container_width=True):
                new_status = "Active" if strategy['status'] == 'Paused' else "Paused"
                st.success(f"✅ Strategy {new_status.lower()}")
        
        with col4:
            if st.button("🔄 Restart", key=f"restart_{strategy['name']}", use_container_width=True):
                st.info(f"🔄 Restarting {strategy['name']}")
        
        with col5:
            if st.button("🗑️ Delete", key=f"delete_{strategy['name']}", use_container_width=True):
                st.warning(f"⚠️ Delete {strategy['name']}?")
        
        st.markdown("---")

def show_live_trading():
    """Live trading interface"""
    st.markdown('<div class="section-header-pro">⚡ Live Trading Dashboard</div>', unsafe_allow_html=True)
    
    # Live status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    live_metrics = [
        ("🟢 Online", "Market Status", "positive"),
        ("3", "Active Strategies", "positive"),
        ("₹1,245", "Today's P&L", "positive"),
        ("12", "Trades Today", "neutral")
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, (value, label, status) in enumerate(live_metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card-pro">
                <div class="metric-value-pro metric-{status}">{value}</div>
                <div class="metric-label-pro">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Live features showcase
    st.markdown("""
    <div class="dashboard-card">
        <h3>🚧 Live Trading Features (Coming Soon)</h3>
        <p>We're building the most advanced live trading platform with the following features:</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0;">
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>📡 Real-time Data</h4>
                <p>Live market data feeds from multiple exchanges</p>
            </div>
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>⚡ Instant Execution</h4>
                <p>Ultra-low latency order execution</p>
            </div>
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>🛡️ Risk Controls</h4>
                <p>Advanced risk management and position limits</p>
            </div>
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>📊 Live Monitoring</h4>
                <p>Real-time performance tracking and alerts</p>
            </div>
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>🔄 Auto-scaling</h4>
                <p>Dynamic position sizing based on market conditions</p>
            </div>
            <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <h4>📱 Mobile Alerts</h4>
                <p>Push notifications and SMS alerts</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 2rem 0;">
            <h4>🎯 Beta Launch: Q4 2024</h4>
            <p>Join our waitlist to get early access to live trading features!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Waitlist signup
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📧 Join Beta Waitlist")
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        if st.button("🚀 Join Waitlist", use_container_width=True, type="primary"):
            if email:
                st.success("✅ Added to waitlist! We'll notify you when live trading is available.")
            else:
                st.error("❌ Please enter a valid email address")

def main():
    """Main application controller"""
    # Check backend connection
    if not check_backend_connection():
        st.error("🔌 Backend Connection Failed")
        st.markdown("""
        <div class="dashboard-card">
            <h4>❌ Backend Server Not Connected</h4>
            <p>Please ensure the FastAPI backend is running on port 8000.</p>
            <p><strong>To start the backend:</strong></p>
            <code>cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create header and navigation
    create_professional_header()
    create_navigation()
    
    # Route to appropriate page
    page_router = {
        'overview': show_dashboard,
        'strategy': show_strategy_builder,
        'backtest': show_strategy_builder,
        'results': show_results_page,
        'portfolio': show_portfolio_page,
        'live': show_live_trading
    }
    
    current_page = st.session_state.get('current_page', 'overview')
    if current_page in page_router:
        page_router[current_page]()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
