import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Smart Financial Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# API endpoints
API_URL = "http://localhost:8000/api"

def login(username: str, password: str):
    try:
        response = requests.post(
            f"{API_URL}/auth/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.token = data["access_token"]
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def main():
    st.title("Smart Financial Analyzer 📈")
    
    # Login sidebar
    with st.sidebar:
        if not st.session_state.authenticated:
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            if st.button("Register"):
                try:
                    response = requests.post(
                        f"{API_URL}/auth/register",
                        data={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Registration failed")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
            return
        
        st.success(f"Welcome {st.session_state.username}! 👋")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    # Main content
    if st.session_state.authenticated:
        tab1, tab2, tab3 = st.tabs(["Financial Analysis", "Stock Analysis", "Portfolio Analysis"])
        
        with tab1:
            st.header("Financial Analysis")
            query = st.text_area("Ask your financial question:", height=100)
            if st.button("Analyze"):
                with st.spinner("Analyzing..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/analysis/analyze",
                            json={
                                "query_type": "generic",
                                "user_input": query
                            }
                        )
                        if response.status_code == 200:
                            st.write(response.json()["result"])
                        else:
                            st.error("Analysis failed")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
        
        with tab2:
            st.header("Stock Analysis")
            symbol = st.text_input("Enter stock symbol (e.g., AAPL):")
            if symbol:
                try:
                    response = requests.get(f"{API_URL}/analysis/stock/{symbol}")
                    if response.status_code == 200:
                        data = response.json()
                        df = pd.DataFrame(data["data"])
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=df.index,
                            open=df['1. open'],
                            high=df['2. high'],
                            low=df['3. low'],
                            close=df['4. close']
                        )])
                        
                        fig.update_layout(
                            title=f"{symbol} Stock Price",
                            yaxis_title="Price",
                            template="plotly_dark"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Failed to fetch stock data")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with tab3:
            st.header("Portfolio Analysis")
            portfolio = st.text_area("Enter your portfolio details:", height=150)
            query = st.text_area("What would you like to analyze about your portfolio?", height=100)
            
            if st.button("Analyze Portfolio"):
                with st.spinner("Analyzing portfolio..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/analysis/analyze",
                            json={
                                "query_type": "portfolio",
                                "user_input": query,
                                "portfolio_details": portfolio
                            }
                        )
                        if response.status_code == 200:
                            st.write(response.json()["result"])
                        else:
                            st.error("Portfolio analysis failed")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()
