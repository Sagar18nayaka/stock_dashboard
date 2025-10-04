import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import time

st.title("📊 Real-Time Stock Market Dashboard")

ticker = st.text_input("Enter Stock Symbol", "AAPL")

if ticker:
    stock = yf.Ticker(ticker)
    data = yf.download(ticker, period="5d", interval="1h")

    if not data.empty:
        # Check if columns are multi-indexed, flatten if yes
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        st.write("### Latest Stock Data")
        st.write(f"**Open:** {data['Open'].iloc[0]:.2f}")
        st.write(f"**High:** {data['High'].iloc[0]:.2f}")
        st.write(f"**Low:** {data['Low'].iloc[0]:.2f}")
        st.write(f"**Close:** {data['Close'].iloc[0]:.2f}")
        st.write(f"**Volume:** {int(data['Volume'].iloc[0])}")

        percent_change = ((data['Close'].iloc[0] - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100
        st.write(f"**Percent Change:** {percent_change:.2f}%")

        st.write("---")

        st.write("### Recent Stock Price (5 days, 1h interval)")
        fig = px.line(data, x=data.index, y="Close", title=f"{ticker} Stock Price")
        st.plotly_chart(fig)
    else:
        st.error("No recent data found. Please enter a valid stock symbol.")

    st.write("---")

    st.write("### Historical Data")
    period = st.selectbox("Select Time Range", ["1 Month", "3 Months", "6 Months", "1 Year"])

    period_dict = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y"
    }

    hist_data = stock.history(period=period_dict[period])

    if not hist_data.empty:
        st.line_chart(hist_data['Close'])

        hist_data['SMA_20'] = hist_data['Close'].rolling(window=20).mean()
        hist_data['EMA_20'] = hist_data['Close'].ewm(span=20, adjust=False).mean()

        st.write("### Historical Data with Moving Averages (20 days)")
        st.line_chart(hist_data[['Close', 'SMA_20', 'EMA_20']])
    else:
        st.error("No historical data available for this period.")

    st.write("---")

    st.write("### Auto-Refresh")
    refresh_interval = st.slider("Refresh every (seconds)", min_value=10, max_value=300, value=60, step=10)

    time.sleep(refresh_interval)
    st.experimental_rerun()

    st.write("---")
    st.write("### Export Historical Data")
    csv = hist_data.to_csv().encode('utf-8')

    st.download_button(
        label="Download Historical Data as CSV",
        data=csv,
        file_name=f"{ticker}_historical_data.csv",
        mime='text/csv'
    )
