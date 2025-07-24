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

# Page configuration - Professional layout like AlgoTest
st.set_page_config(
    page_title="AlgoBacktest Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling inspired by AlgoTest
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom CSS for professional look */
    .main-container {
        padding: 0;
        margin: 0;
    }
    
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        color: white;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .nav-tabs {
        background: white;
        border-bottom: 2px solid #f0f2f6;
        padding: 0 2rem;
        margin: 0 -1rem 2rem -1rem;
    }
    
    .nav-tab {
        display: inline-block;
        padding: 1rem 2rem;
        margin-right: 0.5rem;
        border-bottom: 3px solid transparent;
        color: #666;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
    }
    
    .nav-tab.active {
        color: #667eea;
        border-bottom-color: #667eea;
        background: #f8f9fa;
    }
    
    .strategy-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .strategy-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-positive {
        color: #27ae60 !important;
    }
    
    .metric-negative {
        color: #e74c3c !important;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #7f8c8d;
        line-height: 1.6;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    /* Custom Plotly styling */
    .js-plotly-plot .plotly .modebar {
        right: 10px !important;
    }
    
    /* Table styling */
    .dataframe {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #f8f9fa;
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* Upload area styling */
    .uploadedFile {
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
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
    """Create professional header section"""
    st.markdown("""
    <div class="header-section">
        <div class="header-title">AlgoBacktest Pro</div>
        <div class="header-subtitle">Professional Stock Market Backtesting Platform</div>
    </div>
    """, unsafe_allow_html=True)

def create_navigation():
    """Create navigation tabs"""
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 2])
    
    with col1:
        if st.button("📊 Overview", use_container_width=True):
            st.session_state.current_page = 'overview'
    
    with col2:
        if st.button("⚙️ Strategy Builder", use_container_width=True):
            st.session_state.current_page = 'strategy'
    
    with col3:
        if st.button("🚀 Backtest", use_container_width=True):
            st.session_state.current_page = 'backtest'
    
    with col4:
        if st.button("📈 Results", use_container_width=True):
            st.session_state.current_page = 'results'
    
    with col5:
        if st.button("💾 Portfolio", use_container_width=True):
            st.session_state.current_page = 'portfolio'
    
    with col6:
        if st.button("⚡ Live Trading", use_container_width=True):
            st.session_state.current_page = 'live'

def show_overview_page():
    """Professional overview page similar to AlgoTest"""
    st.markdown('<div class="section-header">Platform Overview</div>', unsafe_allow_html=True)
    
    # Key metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value metric-positive">₹1,24,750</div>
            <div class="metric-label">Total P&L</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">78.4%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,247</div>
            <div class="metric-label">Total Trades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value metric-negative">-₹8,450</div>
            <div class="metric-label">Max Drawdown</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature grid
    st.markdown('<div class="section-header">Why Choose AlgoBacktest Pro?</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Lightning Fast</div>
            <div class="feature-desc">Process years of data in seconds with our optimized backtesting engine</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Precision Accurate</div>
            <div class="feature-desc">Realistic trading costs including slippage, brokerage, and taxes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Advanced Analytics</div>
            <div class="feature-desc">Comprehensive performance metrics and risk analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start section
    st.markdown('<div class="section-header">Quick Start</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="strategy-card">
            <h4>Ready to Get Started?</h4>
            <p>Create your first strategy in under 5 minutes:</p>
            <ol>
                <li>Upload your market data and trade signals</li>
                <li>Configure strategy parameters</li>
                <li>Run backtest and analyze results</li>
                <li>Optimize and deploy for live trading</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚀 Start Backtesting", key="start_bt", use_container_width=True):
            st.session_state.current_page = 'strategy'
            st.rerun()

def show_strategy_builder():
    """Strategy builder page similar to AlgoTest interface"""
    st.markdown('<div class="section-header">Strategy Builder</div>', unsafe_allow_html=True)
    
    # Strategy configuration in professional layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">📁 Data Upload</div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploads
        market_file = st.file_uploader(
            "Market Data (CSV)", 
            type=['csv'], 
            help="Upload OHLC market data"
        )
        
        trade_file = st.file_uploader(
            "Trade Signals (CSV/XLSX)", 
            type=['csv', 'xlsx'], 
            help="Upload your trading signals"
        )
        
        # Upload status
        if market_file and trade_file:
            st.markdown('<span class="status-badge status-success">✓ Files Ready</span>', unsafe_allow_html=True)
        elif market_file or trade_file:
            st.markdown('<span class="status-badge status-warning">⚠ Missing File</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-error">✗ No Files</span>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">⚙️ Strategy Parameters</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Basic parameters
        col2a, col2b = st.columns(2)
        
        with col2a:
            sl_pct = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
            target_pct = st.number_input("Target (%)", min_value=0.1, max_value=100.0, value=4.0, step=0.1)
        
        with col2b:
            position_size = st.number_input("Position Size", min_value=1, max_value=1000, value=100)
            max_loss = st.number_input("Daily Loss Limit", min_value=0, max_value=100000, value=5000)
    
    # Advanced settings
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🔧 Advanced Settings</div>
    </div>
    """, unsafe_allow_html=True)
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown("**Trailing Stop**")
        enable_trailing = st.checkbox("Enable", value=False, key="trailing")
        if enable_trailing:
            trail_trigger = st.number_input("Trigger %", min_value=0.1, max_value=20.0, value=1.5, step=0.1)
            trail_lock = st.number_input("Lock %", min_value=0.1, max_value=10.0, value=0.5, step=0.1)
        else:
            trail_trigger = None
            trail_lock = None
    
    with col4:
        st.markdown("**Re-entry Logic**")
        enable_reentry = st.checkbox("Enable", value=False, key="reentry")
        if enable_reentry:
            reentry_count = st.number_input("Max Re-entries", min_value=1, max_value=10, value=2)
            reentry_mode = st.selectbox("Mode", ["RE-IMMEDIATE", "RE-DELAYED"])
        else:
            reentry_count = 0
            reentry_mode = None
    
    with col5:
        st.markdown("**Trading Costs**")
        slippage = st.number_input("Slippage (₹)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
        brokerage = st.number_input("Brokerage (₹)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.1)
    
    # Action buttons
    st.markdown("---")
    col6, col7, col8 = st.columns([1, 1, 1])
    
    with col6:
        if st.button("💾 Save Strategy", use_container_width=True):
            st.success("Strategy saved successfully!")
    
    with col7:
        if st.button("📊 Preview", use_container_width=True):
            st.info("Strategy preview will be shown here")
    
    with col8:
        if st.button("🚀 Run Backtest", use_container_width=True, type="primary"):
            if market_file and trade_file:
                # Upload files
                with st.spinner("Uploading files..."):
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
                        "position_size": position_size,
                        "slippage": slippage,
                        "brokerage": brokerage,
                        "tax_rate": tax_rate,
                        "max_loss_per_day": max_loss
                    }
                    
                    # Run backtest
                    with st.spinner("Running backtest..."):
                        result = run_backtest_api(config)
                    
                    if result:
                        st.session_state.backtest_results = result
                        st.session_state.current_page = 'results'
                        st.success("Backtest completed! Check Results tab.")
                        st.rerun()
                    else:
                        st.error("Backtest failed!")
                else:
                    st.error("File upload failed!")
            else:
                st.error("Please upload both market data and trade signals!")

def show_results_page():
    """Professional results page similar to AlgoTest"""
    if not st.session_state.backtest_results:
        st.markdown('<div class="section-header">No Results Available</div>', unsafe_allow_html=True)
        st.info("Run a backtest first to see results here.")
        return
    
    result = st.session_state.backtest_results
    summary = result['summary']
    trade_log = result['trade_log']
    equity_curve = result['equity_curve']
    
    st.markdown('<div class="section-header">Backtest Results</div>', unsafe_allow_html=True)
    
    # Key performance metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        pnl_class = "metric-positive" if summary['total_pnl'] > 0 else "metric-negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {pnl_class}">₹{summary['total_pnl']:,.0f}</div>
            <div class="metric-label">Total P&L</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary['win_rate']*100:.1f}%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary['num_trades']}</div>
            <div class="metric-label">Total Trades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dd_class = "metric-negative" if summary['max_drawdown'] < 0 else "metric-value"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {dd_class}">₹{summary['max_drawdown']:,.0f}</div>
            <div class="metric-label">Max Drawdown</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        pf = summary.get('profit_factor', 0)
        pf_display = "∞" if pf == float('inf') else f"{pf:.2f}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pf_display}</div>
            <div class="metric-label">Profit Factor</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Equity curve
        if equity_curve:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(equity_curve))),
                y=equity_curve,
                mode='lines',
                name='Equity Curve',
                line=dict(color='#667eea', width=3),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title="Equity Curve",
                xaxis_title="Trade Number",
                yaxis_title="Cumulative P&L (₹)",
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # P&L distribution pie chart
        if trade_log:
            wins = len([t for t in trade_log if t['pnl'] > 0])
            losses = len([t for t in trade_log if t['pnl'] <= 0])
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Wins', 'Losses'],
                values=[wins, losses],
                marker_colors=['#27ae60', '#e74c3c'],
                hole=0.4
            )])
            
            fig_pie.update_layout(
                title="Win/Loss Distribution",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Additional metrics
    st.markdown('<div class="section-header">Detailed Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Win", f"₹{summary.get('avg_win', 0):,.2f}")
        st.metric("Winning Trades", summary.get('winning_trades', 0))
    
    with col2:
        st.metric("Average Loss", f"₹{summary.get('avg_loss', 0):,.2f}")
        st.metric("Losing Trades", summary.get('losing_trades', 0))
    
    with col3:
        st.metric("Sharpe Ratio", f"{summary.get('sharpe_ratio', 0):.2f}")
        st.metric("Max Consecutive Wins", summary.get('max_consecutive_wins', 0))
    
    with col4:
        st.metric("Total Return %", f"{summary.get('total_return_pct', 0):.2f}%")
        st.metric("Max Consecutive Losses", summary.get('max_consecutive_losses', 0))
    
    # Trade log table
    st.markdown('<div class="section-header">Trade Log</div>', unsafe_allow_html=True)
    
    if trade_log:
        df = pd.DataFrame(trade_log)
        
        # Select important columns for display
        display_cols = ['date', 'time', 'direction', 'entry_price', 'exit_price', 'pnl', 'max_profit_pct']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            df_display.columns = ['Date', 'Time', 'Direction', 'Entry', 'Exit', 'P&L', 'Max Profit %']
            
            # Format numeric columns
            df_display['Entry'] = df_display['Entry'].round(2)
            df_display['Exit'] = df_display['Exit'].round(2)
            df_display['P&L'] = df_display['P&L'].round(2)
            
            st.dataframe(df_display, use_container_width=True, height=300)
        else:
            st.dataframe(df, use_container_width=True, height=300)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Report",
            data=csv,
            file_name=f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def show_portfolio_page():
    """Portfolio management page"""
    st.markdown('<div class="section-header">Strategy Portfolio</div>', unsafe_allow_html=True)
    
    # Sample strategies
    strategies = [
        {
            "name": "Momentum Breakout",
            "status": "Active",
            "pnl": 45750,
            "win_rate": 78.4,
            "trades": 156,
            "created": "2024-01-15"
        },
        {
            "name": "Mean Reversion",
            "status": "Paused",
            "pnl": -8240,
            "win_rate": 42.1,
            "trades": 89,
            "created": "2024-02-03"
        },
        {
            "name": "RSI Oversold",
            "status": "Active",
            "pnl": 23150,
            "win_rate": 65.2,
            "trades": 234,
            "created": "2024-01-28"
        }
    ]
    
    for strategy in strategies:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{strategy['name']}**")
            st.caption(f"Created: {strategy['created']}")
        
        with col2:
            status_class = "status-success" if strategy['status'] == "Active" else "status-warning"
            st.markdown(f'<span class="status-badge {status_class}">{strategy["status"]}</span>', unsafe_allow_html=True)
        
        with col3:
            pnl_color = "🟢" if strategy['pnl'] > 0 else "🔴"
            st.metric("P&L", f"{pnl_color} ₹{strategy['pnl']:,}")
        
        with col4:
            st.metric("Win Rate", f"{strategy['win_rate']}%")
        
        with col5:
            st.metric("Trades", strategy['trades'])
        
        with col6:
            if st.button("View", key=f"view_{strategy['name']}"):
                st.info(f"Viewing {strategy['name']} details...")
        
        st.markdown("---")

def show_live_trading():
    """Live trading simulation page"""
    st.markdown('<div class="section-header">Live Trading</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="strategy-card">
        <h3>🚧 Coming Soon</h3>
        <p>Live trading functionality will be available in the next update. Features will include:</p>
        <ul>
            <li>Real-time market data integration</li>
            <li>Automated order execution</li>
            <li>Risk management controls</li>
            <li>Live performance monitoring</li>
        </ul>
        <p>Stay tuned for updates!</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application with professional navigation"""
    # Check backend connection
    if not check_backend_connection():
        st.error("🔌 Backend server not connected. Please start the FastAPI backend.")
        st.code("cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Create professional header
    create_professional_header()
    
    # Create navigation
    create_navigation()
    
    # Show current page
    if st.session_state.current_page == 'overview':
        show_overview_page()
    elif st.session_state.current_page == 'strategy':
        show_strategy_builder()
    elif st.session_state.current_page == 'backtest':
        show_strategy_builder()  # Same as strategy for now
    elif st.session_state.current_page == 'results':
        show_results_page()
    elif st.session_state.current_page == 'portfolio':
        show_portfolio_page()
    elif st.session_state.current_page == 'live':
        show_live_trading()

if __name__ == "__main__":
    main()
