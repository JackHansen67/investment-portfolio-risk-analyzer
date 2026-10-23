# Project 2: Investment Portfolio Risk Analyzer

A functional FinTech prototype that models portfolio concentration, downside volatility, and historical drawdowns across multi-asset allocations relative to standard market benchmarks.

---

## Financial Concepts & Calculations Implemented

1. **Annualized Portfolio Return & Volatility:**
   - Compounded using a standard 252-trading-day convention:
     $$\text{Annual Return} = \bar{R}_{\text{daily}} \times 252, \quad \sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$
2. **Sharpe Ratio:**
   - Measures excess portfolio return per unit of total risk over the user-defined risk-free rate ($R_f$):
     $$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$
3. **Sortino Ratio:**
   - Isolates downside volatility ($\sigma_d$) to ensure positive upside spikes do not artificially penalize the score:
     $$\text{Sortino} = \frac{R_p - R_f}{\sigma_d}$$
4. **Maximum Drawdown:**
   - Identifies the worst historical peak-to-trough decline over the selected time horizon:
     $$\text{Max Drawdown} = \min \left( \frac{P_t - \max_{s \le t} P_s}{\max_{s \le t} P_s} \right)$$

---

## APIs and Datasets Used

- **Yahoo Finance (`yfinance`):** Historical adjusted close prices, dividend adjustments, and benchmark indices (`SPY`, `^GSPC`, `^QQQ`).
- **Finnhub API:** Company profile and industry classifications.
- **Defensive Data Handling:** Automated weight normalization, missing ticker filtering, inverted date validation, and zero-variance math exceptions.

---

## Role of the AI Coding Agent

This application was engineered using **Google Antigravity**:
- **Scaffolding & UI:** Antigravity structured the Streamlit application layout, dynamic weight normalization sliders, and Plotly interactive visualizations.
- **Vectorized Mathematics:** Antigravity generated vectorized matrix multiplications via NumPy and Pandas to efficiently calculate weighted portfolio returns and downside deviation.
- **Error Handling:** Designed fallback routines for missing ticker symbols and unexpected API downtime.

---

## Known Limitations & Incomplete Features

1. **Rebalancing Frequency:** The model assumes constant static weights over time rather than modeling discrete monthly or annual rebalancing schedules.
2. **Tax & Transaction Costs:** Does not account for capital gains taxes, brokerage commissions, or bid-ask spread slippage.
3. **Fixed Risk-Free Rate:** Uses a constant input rate rather than matching historical daily Treasury yields.

---

## Reproducibility & Setup Instructions

### Prerequisites
- Python 3.9+
- Git

### Installation
1. Clone this repository:
   ```bash
   git clone [https://github.com/JackHansen67/investment-portfolio-risk-analyzer.git](https://github.com/JackHansen67/investment-portfolio-risk-analyzer.git)
   cd investment-portfolio-risk-analyzer