import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os

# Page configuration with custom theme
st.set_page_config(
    page_title="Smart Financial Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #262730;
        color: white;
    }
    .stSelectbox>div>div>div {
        background-color: #262730;
        color: white;
    }
    div.block-container {
        padding-top: 2rem;
    }
    div.element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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
    # Sidebar with gradient background
    with st.sidebar:
        st.markdown("""
            <div style='background: linear-gradient(45deg, #FF4B4B, #9F2B68);
                        padding: 2rem 1rem;
                        border-radius: 10px;
                        margin-bottom: 2rem;'>
                <h1 style='color: white; text-align: center; margin: 0;'>
                    📈 Smart Finance
                </h1>
            </div>
        """, unsafe_allow_html=True)

        if not st.session_state.authenticated:
            st.markdown("### Welcome! 👋")
            st.markdown("Please login to access the analyzer.")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    if login(username, password):
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            if st.button("Register New Account"):
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

        st.success(f"Welcome back, {st.session_state.username}! 👋")
        if st.button("Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

    # Main content
    if st.session_state.authenticated:
        st.title("Smart Financial Analyzer")
        st.markdown("""
            <div style='background: linear-gradient(45deg, #262730, #1E1E1E);
                        padding: 1rem;
                        border-radius: 10px;
                        margin-bottom: 2rem;'>
                <p style='color: #FAFAFA; margin: 0;'>
                    Get AI-powered financial insights, portfolio analysis, and market trends.
                </p>
            </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["📊 Analysis", "💹 Stocks", "📂 Portfolio"])

        with tabs[0]:
            st.header("Financial Analysis")
            query = st.text_area(
                "What would you like to know?",
                placeholder="e.g., What are the best investment strategies for a recession?",
                height=100
            )

            col1, col2 = st.columns(2)
            with col1:
                include_news = st.checkbox("Include latest news", value=True)
            with col2:
                include_books = st.checkbox("Include book insights", value=True)

            if st.button("Analyze", use_container_width=True):
                with st.spinner("Analyzing your query..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/analysis/analyze",
                            json={
                                "query_type": "generic",
                                "user_input": query,
                                "include_news": include_news,
                                "include_books": include_books
                            }
                        )
                        if response.status_code == 200:
                            result = response.json()["result"]
                            st.markdown(
                                f"""<div style='background: #262730; 
                                            padding: 1.5rem; 
                                            border-radius: 10px;
                                            border-left: 5px solid #FF4B4B;'>
                                    {result}
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Analysis failed")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

        with tabs[1]:
            st.header("Stock Analysis")
            col1, col2 = st.columns([3, 1])
            with col1:
                symbol = st.text_input("Enter stock symbol:", placeholder="e.g., AAPL")
            with col2:
                interval = st.selectbox("Time interval:", ["1D", "1W", "1M", "3M", "1Y"])

            if symbol:
                with st.spinner("Fetching stock data..."):
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
                                yaxis_title="Price ($)",
                                template="plotly_dark",
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                xaxis_rangeslider_visible=False
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # Show key statistics
                            st.markdown("### Key Statistics")
                            stats_cols = st.columns(4)
                            with stats_cols[0]:
                                st.metric("Open", f"${df['1. open'].iloc[-1]:.2f}")
                            with stats_cols[1]:
                                st.metric("Close", f"${df['4. close'].iloc[-1]:.2f}")
                            with stats_cols[2]:
                                st.metric("High", f"${df['2. high'].iloc[-1]:.2f}")
                            with stats_cols[3]:
                                st.metric("Low", f"${df['3. low'].iloc[-1]:.2f}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with tabs[2]:
            st.header("Portfolio Analysis")

            portfolio = st.text_area(
                "Enter your portfolio details:",
                placeholder="Example:\nStocks: 40% (AAPL 15%, MSFT 15%, GOOGL 10%)\nBonds: 30%\nCash: 30%",
                height=150
            )

            query = st.text_area(
                "What would you like to analyze about your portfolio?",
                placeholder="e.g., How can I optimize my portfolio for the current market conditions?",
                height=100
            )

            if st.button("Analyze Portfolio", use_container_width=True):
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
                            result = response.json()["result"]
                            st.markdown(
                                f"""<div style='background: #262730; 
                                            padding: 1.5rem; 
                                            border-radius: 10px;
                                            border-left: 5px solid #FF4B4B;'>
                                    {result}
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Portfolio analysis failed")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()