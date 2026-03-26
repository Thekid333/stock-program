import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytz
import streamlit as st
import plotly.graph_objs as go
from alpaca_trade_api.rest import REST, TimeFrame

# ─── 1. Alpaca credentials ───────────────────────────────────────────────────────
API_KEY    = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL   = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

if not API_KEY or not API_SECRET:
    st.error("🚨 Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY in your environment.")
    st.stop()

# ─── 2. Init Alpaca client ───────────────────────────────────────────────────────
alpaca = REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

# ─── 3. Timezones ────────────────────────────────────────────────────────────────
UTC       = pytz.UTC
MOUNTAIN  = pytz.timezone("America/Denver")

# ─── 4. Streamlit layout ────────────────────────────────────────────────────────
st.set_page_config(page_title="AAPL 24 h Candles", layout="wide")
st.title("📈 AAPL 1 Min Candles (Last 24 Hours — Denver Time)")

# Create two columns and placeholders **once**:
overview_col, chart_col = st.columns([1, 3])
symbol_ph   = overview_col.empty()
price_ph    = overview_col.empty()
chart_ph    = chart_col.empty()

symbol    = "AAPL"
timeframe = TimeFrame.Minute
interval  = 60    # seconds between updates

while True:
    try:
        # ─── 5a. Compute 24 h window in UTC ────────────────────────────────────
        now_utc     = datetime.now(timezone.utc)
        ago_24h_utc = now_utc - timedelta(hours=24)

        # ─── 5b. Fetch bars via IEX feed ─────────────────────────────────────
        bars = alpaca.get_bars(
            symbol,
            timeframe,
            start=ago_24h_utc.isoformat(),
            end=now_utc.isoformat(),
            feed="iex"
        ).df

        # ─── 5c. Flatten MultiIndex if needed ─────────────────────────────────
        df = bars.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                lvl1 if lvl1 in {"open","high","low","close"} else lvl2
                for lvl1, lvl2 in df.columns
            ]

        # ─── 5d. Timezone: UTC→Denver & drop tz ───────────────────────────────
        idx = pd.to_datetime(df.index)
        if idx.tz is None:
            idx = idx.tz_localize(UTC)
        df.index = idx.tz_convert(MOUNTAIN).tz_localize(None)

        # ─── 5e. Build OHLC + current price ───────────────────────────────────
        ohlc = df[["open","high","low","close"]]
        current_price = ohlc["close"].iloc[-1]

        # ─── 5f. Update overview placeholders (same ones) ─────────────────────
        symbol_ph.metric("Symbol", symbol)
        price_ph.metric("Current Price", f"${current_price:.2f}")

        # ─── 5g. Build and update chart placeholder ───────────────────────────
        fig = go.Figure(
            data=[go.Candlestick(
                x=ohlc.index,
                open=ohlc["open"],
                high=ohlc["high"],
                low=ohlc["low"],
                close=ohlc["close"],
                name=symbol
            )]
        )
        fig.update_layout(
            title="",
            xaxis=dict(rangeslider=dict(visible=True)),
            margin=dict(l=10, r=10, t=20, b=10)
        )
        chart_ph.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Error fetching or plotting data: {e}")

    time.sleep(interval)
