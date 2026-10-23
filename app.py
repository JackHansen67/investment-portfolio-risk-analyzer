import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import finnhub
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(
    page_title="Investment Portfolio Risk Analyzer",
    page_icon="📊",
    layout="wide"
)

# ----------------- SIDEBAR: User Parameters (Req 3) -----------------
st.sidebar.header("Portfolio Configuration")

# Finnhub API Key (Optional user input or demo fallback)
finnhub_key = st.sidebar.text_input(
    "Finnhub API Key (Optional for profiles):",
    type="password",
    help="Enter your free Finnhub API key from https://finnhub.io/ to load real-time company metadata."
)

tickers_input = st.sidebar.text_input(
    "Holdings (comma-separated, min 3):",
    value="AAPL, MSFT, SPY"
)

selected_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

benchmark = st.sidebar.selectbox("Benchmark Index", ["SPY", "^GSPC", "^QQQ"], index=0)

col_d1, col_d2 = st.sidebar.columns(2)
start_date = col_d1.date_input("Start Date", datetime.today() - timedelta(days=365 * 2))
end_date = col_d2.date_input("End Date", datetime.today())

rf_rate = st.sidebar.number_input(
    "Risk-Free Rate (Annualized %)",
    min_value=0.0,
    max_value=15.0,
    value=4.5,
    step=0.1
) / 100.0

# Dynamic Weight Allocation
st.sidebar.subheader("Portfolio Weighting (%)")
weights = []
if len(selected_tickers) >= 3:
    default_w = round(100.0 / len(selected_tickers), 1)
    for ticker in selected_tickers:
        w = st.sidebar.number_input(f"{ticker} Weight (%)", min_value=0.0, max_value=100.0, value=default_w, step=1.0)
        weights.append(w)
    
    total_weight = sum(weights)
    if not np.isclose(total_weight, 100.0, atol=0.5):
        st.sidebar.warning(f"⚠️ Total Weight is {total_weight:.1f}%. Weights will be normalized to 100%.")

# ----------------- VALIDATION & DATA FETCHING (Req 2 & 6) -----------------
if len(selected_tickers) < 3:
    st.error("Project 2 requires at least 3 stocks or ETFs. Please add more tickers in the sidebar.")
    st.stop()

if start_date >= end_date:
    st.error("Start Date must precede End Date.")
    st.stop()

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_portfolio_data(symbols, benchmark_sym, start, end):
    all_syms = list(set(symbols + [benchmark_sym]))
    try:
        data = yf.download(all_syms, start=start, end=end, auto_adjust=True)
        if data.empty:
            return None, "No market data returned. Please verify ticker symbols."
        
        close_df = data["Close"] if "Close" in data.columns else data
        if isinstance(close_df, pd.Series):
            close_df = close_df.to_frame(name=all_syms[0])
            
        close_df = close_df.dropna(how="all", axis=1)
        return close_df, None
    except Exception as e:
        return None, f"Error fetching market data: {str(e)}"

with st.spinner("Retrieving financial market series..."):
    prices_raw, err = fetch_portfolio_data(selected_tickers, benchmark, start_date, end_date)

if err:
    st.error(err)
    st.stop()

# Check that holdings exist in returned dataset
valid_holdings = [t for t in selected_tickers if t in prices_raw.columns]
if len(valid_holdings) < 3:
    st.error(f"Could only retrieve data for {len(valid_holdings)} valid ticker(s). Please check for misspelled symbols.")
    st.stop()

# Clean price data
prices = prices_raw[valid_holdings].dropna()
bench_prices = prices_raw[benchmark].dropna() if benchmark in prices_raw.columns else None

# Normalize weights
norm_weights = np.array([weights[selected_tickers.index(t)] for t in valid_holdings])
if norm_weights.sum() > 0:
    norm_weights = norm_weights / norm_weights.sum()
else:
    norm_weights = np.repeat(1.0 / len(valid_holdings), len(valid_holdings))

# ----------------- FINANCIAL CALCULATIONS (Req 4) -----------------
trading_days = 252

# Daily Returns
asset_returns = prices.pct_change().dropna()
portfolio_daily_returns = asset_returns.dot(norm_weights)

# 1. Cumulative Performance
cum_asset_returns = (1 + asset_returns).cumprod()
cum_portfolio_returns = (1 + portfolio_daily_returns).cumprod()

# 2. Annualized Return & Annualized Volatility
ann_portfolio_return = portfolio_daily_returns.mean() * trading_days
ann_portfolio_vol = portfolio_daily_returns.std() * np.sqrt(trading_days)

# 3. Sharpe & Sortino Ratios
excess_returns = portfolio_daily_returns - (rf_rate / trading_days)
sharpe_ratio = (portfolio_daily_returns.mean() * trading_days - rf_rate) / ann_portfolio_vol if ann_portfolio_vol != 0 else np.nan

downside_returns = portfolio_daily_returns[portfolio_daily_returns < 0]
downside_dev = downside_returns.std() * np.sqrt(trading_days)
sortino_ratio = (portfolio_daily_returns.mean() * trading_days - rf_rate) / downside_dev if downside_dev != 0 else np.nan

# 4. Maximum Drawdown
running_max = cum_portfolio_returns.cummax()
portfolio_drawdowns = (cum_portfolio_returns - running_max) / running_max
max_drawdown = portfolio_drawdowns.min()

# Benchmark Metrics
if bench_prices is not None:
    bench_returns = bench_prices.pct_change().dropna()
    ann_bench_return = bench_returns.mean() * trading_days
    ann_bench_vol = bench_returns.std() * np.sqrt(trading_days)
    cum_bench = (1 + bench_returns).cumprod()
    bench_dd = ((cum_bench - cum_bench.cummax()) / cum_bench.cummax()).min()
    bench_sharpe = (ann_bench_return - rf_rate) / ann_bench_vol if ann_bench_vol != 0 else np.nan

# ----------------- UI & VISUALIZATIONS (Req 1, 5, 7) -----------------
st.title("📈 Investment Portfolio Risk Analyzer")
st.markdown("Quantify concentration risk, downside volatility, and historical market behavior.")

# Optional Finnhub Company Info Ribbon
if finnhub_key:
    try:
        f_client = finnhub.Client(api_key=finnhub_key)
        profile_cols = st.columns(len(valid_holdings))
        for i, tick in enumerate(valid_holdings):
            prof = f_client.company_profile2(symbol=tick)
            if prof and "name" in prof:
                profile_cols[i].caption(f"**{prof.get('name')}** ({prof.get('finnhubIndustry', 'N/A')})")
    except Exception:
        pass

# Top Level KPI Row
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Annualized Return", f"{ann_portfolio_return:.2%}", delta=f"{(ann_portfolio_return - ann_bench_return):.2%} vs Bench" if bench_prices is not None else None)
k2.metric("Annualized Volatility", f"{ann_portfolio_vol:.2%}", delta=f"{(ann_portfolio_vol - ann_bench_vol):.2%}" if bench_prices is not None else None, delta_color="inverse")
k3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
k4.metric("Sortino Ratio", f"{sortino_ratio:.2f}")
k5.metric("Max Drawdown", f"{max_drawdown:.2%}", delta=f"{(max_drawdown - bench_dd):.2%}" if bench_prices is not None else None, delta_color="normal")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Performance & Risk Charts", "💼 Portfolio Composition", "📖 Methodology & Docs"])

with tab1:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("Cumulative Growth vs. Benchmark")
        comp_df = pd.DataFrame({
            "Portfolio": (cum_portfolio_returns - 1) * 100,
        })
        if bench_prices is not None:
            aligned_bench = cum_bench.reindex(cum_portfolio_returns.index).ffill()
            comp_df[f"Benchmark ({benchmark})"] = (aligned_bench - 1) * 100
            
        fig_perf = px.line(
            comp_df,
            labels={"value": "Total Return (%)", "index": "Date"},
            title="Portfolio vs Benchmark Growth Path"
        )
        fig_perf.update_layout(hovermode="x unified")
        st.plotly_chart(fig_perf, use_container_width=True)
        
    with col_c2:
        st.subheader("Historical Drawdown Profile")
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=portfolio_drawdowns.index,
            y=portfolio_drawdowns * 100,
            fill='tozeroy',
            name='Portfolio Drawdown',
            line=dict(color='firebrick')
        ))
        fig_dd.update_layout(
            title="Peak-to-Trough Drawdown (%)",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_dd, use_container_width=True)

with tab2:
    st.subheader("Target Asset Allocation")
    col_w1, col_w2 = st.columns([1, 1])
    
    with col_w1:
        pie_df = pd.DataFrame({"Ticker": valid_holdings, "Weight": norm_weights * 100})
        fig_pie = px.pie(pie_df, names="Ticker", values="Weight", hole=0.4, title="Holdings Weighting Breakdown")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_w2:
        st.subheader("Individual Asset Risk Contributions")
        asset_vol = asset_returns.std() * np.sqrt(trading_days)
        asset_cum = (1 + asset_returns).cumprod()
        asset_mdd = ((asset_cum - asset_cum.cummax()) / asset_cum.cummax()).min()
        
        breakdown_df = pd.DataFrame({
            "Weight": [f"{w:.1%}" for w in norm_weights],
            "Annual Volatility": asset_vol.map("{:.2%}".format),
            "Max Drawdown": asset_mdd.map("{:.2%}".format)
        }, index=valid_holdings)
        st.dataframe(breakdown_df, use_container_width=True)

with tab3:
    st.header("Application Documentation")
    st.markdown("""
    ### Purpose & Scope
    This application addresses portfolio risk management by illustrating how multi-asset concentration affects total return volatility, tail-risk drawdowns, and risk-adjusted efficiency.
    
    ### Mathematical Formulations
    1. **Annualized Volatility:** Continuous standard deviation of daily logarithmic or percentage returns multiplied by $\\sqrt{252}$.
    2. **Sharpe Ratio:** Evaluates risk premium per unit of total risk: $\\frac{R_p - R_f}{\\sigma_p}$.
    3. **Sortino Ratio:** Evaluates risk premium using downside root-mean-square deviation ($\sigma_d$), penalizing only negative returns.
    4. **Maximum Drawdown:** The maximum cumulative loss from a rolling peak to a subsequent trough.
    
    ### Data Sources & Limitations
    - **APIs:** Market historical prices sourced via Yahoo Finance (`yfinance`); optional company profile telemetry sourced via Finnhub API.
    - **Limitations:** Assumes continuous portfolio rebalancing to target weights with zero transaction friction, bid-ask slippage, or dividend withholding taxes.
    """)