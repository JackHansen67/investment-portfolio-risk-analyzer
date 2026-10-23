# Investment Portfolio & Risk Analyzer

An interactive FinTech web prototype designed to evaluate multi-asset portfolio concentration, estimate downside exposure, and compare risk-adjusted returns against standard market benchmarks.

---

## Application Purpose & Functionality

Evaluating individual assets in isolation often leads investors to underestimate portfolio risk arising from high correlations, sector concentration, and tail-risk drawdowns. This prototype provides an intuitive analytics dashboard where users can:
- Construct multi-asset equity/ETF portfolios (minimum 3 assets).
- Assign customized percentage weights or capital allocations (with automatic normalization).
- Compare portfolio growth trajectories against benchmark market indices (`SPY`, `^GSPC`, `^QQQ`).
- Analyze annualized volatility, downside risk profiles, and risk-adjusted efficiency.

---

## Application Screenshots

### 1. Performance Overview & Risk Summary
![Portfolio Risk Dashboard](<img width="1725" height="386" alt="Screenshot 2026-10-23 123644" src="https://github.com/user-attachments/assets/76787d88-a533-416b-9114-9572fec0d4b6" />)

### 2. Comparative Growth & Drawdown Trajectory
![Visualizations and Drawdown Profile](<img width="1842" height="822" alt="Screenshot 2026-10-23 123728" src="https://github.com/user-attachments/assets/ac1bb96d-e716-4563-a163-eee8109dde21" />)

---

## Financial Concepts & Calculations Implemented

The application performs several quantitative calculations using an annualized 252-trading-day convention:

1. **Annualized Portfolio Return & Volatility:**
   - Evaluates compounded performance and annualized dispersion:
     $$\text{Annual Return} = \bar{R}_{\text{daily}} \times 252$$
     $$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$

2. **Sharpe Ratio:**
   - Measures excess return generated per unit of total risk relative to the user-selected annualized risk-free rate ($R_f$):
     $$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$

3. **Sortino Ratio:**
   - Penalizes only harmful volatility by replacing total standard deviation with downside semi-deviation ($\sigma_d$ for all daily returns $R < 0$):
     $$\text{Sortino} = \frac{R_p - R_f}{\sigma_d}$$

4. **Maximum Drawdown:**
   - Identifies the steepest peak-to-trough decline over the historical evaluation window:
     $$\text{Max Drawdown} = \min \left( \frac{P_t - \max_{s \le t} P_s}{\max_{s \le t} P_s} \right)$$

---

## APIs and Datasets Used

- **Yahoo Finance (`yfinance`):** Primary market data feed supplying historical adjusted close prices, dividend/split adjustments, and broad benchmark index trajectories.
- **Finnhub API:** Supplies real-time company metadata, sector categorization, and profile telemetry.
- **Defensive Error Handling:** Implements exception guards for invalid ticker inputs, empty API responses, inverted date ranges, and zero-variance math exceptions.

---

## Role of the AI Coding Agent

This application was developed collaboratively using **Google Antigravity** as the AI coding agent:
- **UI & Layout Scaffolding:** Antigravity structured the reactive multi-tab Streamlit interface, dynamic weight configuration sliders, and Plotly visualizations.
- **Vectorized Mathematics:** Vectorized matrix multiplications via NumPy and Pandas were implemented to efficiently calculate weighted asset returns and downside volatility.
- **Defensive Data Pipelines:** Antigravity guided the implementation of API error handling, weight normalization checks, and zero-division guards.

---

## Known Limitations & Incomplete Features

1. **Rebalancing Frequency:** Assumes static buy-and-hold weight tracking rather than modeling periodic discrete rebalancing events (e.g., monthly or quarterly).
2. **Friction & Taxes:** Does not account for brokerage transaction fees, bid-ask spreads, slippage, or capital gains taxes.
3. **Constant Risk-Free Rate:** Uses a constant annualized interest rate over the selected window rather than dynamically matching daily Treasury yield curve rates.

---

## Reproducibility & Setup Instructions

Follow these steps to run the application locally or in a cloud workspace:

### Prerequisites
- Python 3.9 or higher
- Git

### Setup & Execution
1. Clone this repository:
   ```bash
   git clone [https://github.com/JackHansen67/investment-portfolio-risk-analyzer.git](https://github.com/JackHansen67/investment-portfolio-risk-analyzer.git)
   cd investment-portfolio-risk-analyzer
