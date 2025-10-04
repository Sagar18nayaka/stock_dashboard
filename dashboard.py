import streamlit as st
import yfinance as yf
import plotly.express as px

st.title("📊 Real-Time Stock Market Dashboard")

ticker = st.text_input("Enter Stock Symbol", "AAPL")

if ticker:
    data = yf.download(ticker, period="5d", interval="1h")
    
    if not data.empty:
        
        data.columns = data.columns.get_level_values(0)

    
        fig = px.line(data, x=data.index, y="Close", title=f"{ticker} Stock Price")
        st.plotly_chart(fig)
    else:
        st.error("No data found. Please enter a valid stock symbol.")
