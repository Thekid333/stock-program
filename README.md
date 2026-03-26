# Stock Program

A real-time stock candlestick dashboard built with **Streamlit**, **Plotly**, and the **Alpaca Markets API**. Fetches live 1-minute OHLC bars and renders an interactive, auto-refreshing candlestick chart directly in your browser.

---

## Features

- Live 1-minute candlestick charts powered by Plotly
- Auto-refreshes every 60 seconds without a full page reload
- Two display modes:
  - **StockDisplay** — shows the last 24 hours of bars, converted to Mountain Time (Denver), with a live current-price metric panel
  - **CandleStickReader** — shows the last 100 bars with a compact single-column layout
- Uses Alpaca's paper-trading endpoint (safe for development — no real money)
- Handles both single-level and MultiIndex DataFrame columns from the Alpaca SDK

---

## Project Structure

```
Stock Program/
├── StockDisplay.py        # 24-hour window, Denver timezone, price overview panel
├── CandleStickReader.py   # Last-N-bars view, env-var credentials
└── README.md
```

---

## Requirements

- Python 3.8+
- [Alpaca Trade API](https://pypi.org/project/alpaca-trade-api/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [pandas](https://pandas.pydata.org/)
- [pytz](https://pypi.org/project/pytz/)

Install all dependencies:

```bash
pip install alpaca-trade-api streamlit plotly pandas pytz
```

---

## Setup

### 1. Get Alpaca API Keys

Sign up for a free paper-trading account at [alpaca.markets](https://alpaca.markets), then generate an API key and secret from the dashboard.

### 2. Set Environment Variables

Both scripts read credentials from environment variables. **Never hardcode secrets in source files.**

```bash
export APCA_API_KEY_ID="your_api_key_here"
export APCA_API_SECRET_KEY="your_api_secret_here"
export APCA_API_BASE_URL="https://paper-api.alpaca.markets"   # optional, this is the default
```

> **Note:** `StockDisplay.py` currently has credentials hardcoded. Before committing or sharing that file, replace the hardcoded values with `os.getenv()` calls the same way `CandleStickReader.py` does.

---

## Usage

### StockDisplay — 24-Hour Chart with Price Panel

```bash
streamlit run StockDisplay.py
```

Opens a wide-layout dashboard with:
- Left column: current symbol and live price metric
- Right column: interactive 1-min candlestick chart for the last 24 hours (Denver / Mountain Time)

### CandleStickReader — Last 100 Bars

```bash
streamlit run CandleStickReader.py
```

Opens a single-column candlestick chart showing the most recent 100 one-minute bars. Range slider is hidden for a cleaner view.

---

## Configuration

Both scripts expose a few easy-to-edit constants at the top of the file:

| Variable    | Default   | Description                                |
|-------------|-----------|--------------------------------------------|
| `symbol`    | `"AAPL"`  | Ticker symbol to track                     |
| `timeframe` | `Minute`  | Bar resolution (`Minute`, `Hour`, `Day`)   |
| `limit`     | `100`     | Number of bars to fetch (CandleStickReader)|
| `interval`  | `60`      | Seconds between auto-refresh polls         |

---

## Security Warning

`StockDisplay.py` currently contains **hardcoded API credentials**. These should be rotated immediately if they have been pushed to any public repository. Replace them with environment variable lookups:

```python
import os
API_KEY    = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
```

Consider adding a `.gitignore` entry for any local `.env` files:

```
.env
*.env
```

---

## License

MIT
