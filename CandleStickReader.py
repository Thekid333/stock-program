import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from alpaca_trade_api.rest import REST, TimeFrame

# ─── 1. Load Alpaca credentials ──────────────────────────────────────────────────
API_KEY    = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL   = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

if not API_KEY or not API_SECRET:
    st.error("🚨 Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY in your environment.")
    st.stop()

# ─── 2. Initialize Alpaca REST client ────────────────────────────────────────────
alpaca = REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# ─── 3. Streamlit UI setup ───────────────────────────────────────────────────────
st.title("📈 Real-Time AAPL Candlestick Chart (1 Min Bars)")
placeholder = st.empty()

symbol    = "AAPL"
timeframe = TimeFrame.Minute
limit     = 100        # how many bars to fetch each update
interval  = 60         # seconds between updates

while True:
    try:
        # ─── 4a. Fetch latest bars ──────────────────────────────────────────────
        bars = alpaca.get_bars(symbol, timeframe, limit=limit).df

        # ─── 4b. Handle both single-level and MultiIndex columns ────────────────
        if isinstance(bars.columns, pd.MultiIndex):
            # old barset: columns like ('AAPL','open'),('AAPL','high'),…
            df = bars.xs(symbol, level=0, axis=1).copy()
        else:
            # new DataFrame: open, high, low, close columns directly
            df = bars.copy()

        # ─── 4c. Clean up index ─────────────────────────────────────────────────
        # remove any timezone so Streamlit/Plotly are happy
        df.index = df.index.tz_localize(None)

        # ─── 5. Build the candlestick figure ────────────────────────────────────
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name=symbol
                )
            ]
        )
        fig.update_layout(
            title=f"{symbol} 1 Min Candles (last {limit})",
            xaxis_rangeslider_visible=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # ─── 6. Render / update chart ────────────────────────────────────────────
        placeholder.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Error fetching data: {e}")

    # ─── 7. Wait until next bar ───────────────────────────────────────────────
    time.sleep(interval)
