import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

#  Page Config & Dark Mode Theme
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #0E1117;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #1A1C23;
        color: white;
    }
    .stDataFrame tbody th, .stDataFrame tbody td {
        color: white;
    }
    .stDownloadButton button {
        background-color: #2E8B57;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Real-Time Stock Market Dashboard")
st.markdown("Track stock prices in real-time, download data, and view historical trends with charts.")

#  Sidebar: Stock Selection
st.sidebar.header("Select Stocks")
stocks_input = st.sidebar.text_input("Enter stock symbols (comma separated)", "AAPL,GOOGL,MSFT,AMZN,TSLA,NVDA")
stock_symbols = [s.strip().upper() for s in stocks_input.split(",")]

#  Sidebar: Refresh Interval
st.sidebar.header("Refresh Settings")
refresh_time = st.sidebar.number_input(
    "Auto-refresh interval (seconds)",
    min_value=10,
    max_value=3600,
    value=60,
    step=10
)

#  Auto-refresh
st_autorefresh(interval=refresh_time * 1000, key="stock_refresh")

#  Fetch & Prepare Stock Data
data_list = []
historical_data = {}
invalid_symbols = []

for symbol in stock_symbols:
    try:
        stock = yf.Ticker(symbol)
        df_stock = stock.history(period="2d")
        df_hist = stock.history(period="30d")
        if df_stock.empty:
            invalid_symbols.append(symbol)
            continue
        last_price = df_stock['Close'].iloc[-1]
        prev_price = df_stock['Close'].iloc[-2] if len(df_stock) > 1 else last_price
        change = last_price - prev_price
        pct_change = (change / prev_price) * 100 if prev_price != 0 else 0
        arrow = "🔺" if change > 0 else ("🔻" if change < 0 else "")
        data_list.append({
            "Stock": symbol,
            "Price": last_price,
            "Change": f"{arrow} {change:.2f}",
            "Percent Change": pct_change
        })
        historical_data[symbol] = df_hist['Close']
    except Exception as e:
        invalid_symbols.append(symbol)

if invalid_symbols:
    st.warning(f"The following symbols are invalid or data unavailable: {', '.join(invalid_symbols)}")

df = pd.DataFrame(data_list)

if not df.empty:
    #  Styled DataFrame
    def color_change(val):
        if "🔺" in str(val):
            color = 'green'
        elif "🔻" in str(val):
            color = 'red'
        else:
            color = 'white'
        return f'color: {color}'

    st.subheader("📊 Stock Prices")

    styled_df = df.style.map(color_change, subset=['Change'])\
                        .background_gradient(subset=['Percent Change'], cmap='RdYlGn', axis=None)\
                        .format({"Percent Change": "{:.2f}%"})

    st.dataframe(styled_df, width='stretch')

    #  Export to CSV
    csv = df.copy()
    csv['Percent Change'] = csv['Percent Change'].apply(lambda x: f"{x:.2f}%")
    csv_file = csv.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_file,
        file_name='stock_data.csv',
        mime='text/csv',
    )

    #  Current Prices Line Chart
    st.subheader("📈 Current Prices")
    st.line_chart(df.set_index("Stock")["Price"])

    #  Percent Change Bar Chart
    st.subheader("📊 Percent Change")
    st.bar_chart(df.set_index("Stock")["Percent Change"])

    #  Historical Charts Per Stock
    st.subheader("📈 Historical Price Charts (Last 30 Days)")
    for symbol, series in historical_data.items():
        st.markdown(f"*{symbol}*")
        st.line_chart(series)

    #  Comparison Chart of All Stocks
    st.subheader("📊 Comparison Chart of All Stocks (Last 30 Days)")
    hist_df = pd.DataFrame(historical_data)
    st.line_chart(hist_df)

    #  Last Updated Timestamp
    st.markdown(f"*Last updated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.warning("No valid stock data available. Check stock symbols.")
