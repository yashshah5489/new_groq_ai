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
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #0E1117 0%, #1A1C24 100%);
        padding: 2rem;
    }

    /* Card styling */
    div[data-testid="stVerticalBlock"] > div {
        background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #FF4B4B 0%, #9F2B68 100%);
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }

    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }

    /* Selectbox styling */
    .stSelectbox>div>div>div {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #FF4B4B 0%, #9F2B68 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E1E1E;
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF4B4B 0%, #9F2B68 100%);
        border: none;
    }

    /* Container spacing */
    div.block-container {
        padding-top: 2rem;
    }

    div.element-container {
        margin-bottom: 1.5rem;
    }

    /* Custom heading styles */
    h1, h2, h3 {
        background: linear-gradient(135deg, #FF4B4B 0%, #9F2B68 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
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
    # Sidebar with modern design
    with st.sidebar:
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #FF4B4B 0%, #9F2B68 100%);
                padding: 2rem;
                border-radius: 16px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                text-align: center;
            '>
                <h1 style='
                    color: white;
                    margin: 0;
                    font-size: 2rem;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                '>
                    📈 Smart Finance
                </h1>
                <p style='
                    color: rgba(255,255,255,0.9);
                    margin-top: 0.5rem;
                    font-size: 1rem;
                '>
                    Your AI Financial Assistant
                </p>
            </div>
        """, unsafe_allow_html=True)

        if not st.session_state.authenticated:
            st.markdown("""
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <h3 style='color: #FF4B4B;'>Welcome! 👋</h3>
                    <p style='color: #FAFAFA;'>Please login to access the analyzer.</p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=True):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Login")
                with col2:
                    register = st.form_submit_button("Register")

                if submitted:
                    if login(username, password):
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                elif register:
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

        # Logged in user info
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                border: 1px solid rgba(255,255,255,0.1);
            '>
                <h4 style='color: #FF4B4B; margin: 0;'>Welcome back!</h4>
                <p style='color: #FAFAFA; margin: 0.5rem 0;'>👤 {st.session_state.username}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

    # Main content
    if st.session_state.authenticated:
        st.title("Smart Financial Analyzer")

        # Welcome card with stats
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
                padding: 2rem;
                border-radius: 16px;
                margin-bottom: 2rem;
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            '>
                <h2 style='color: #FF4B4B; margin: 0;'>Welcome to Your Financial Dashboard</h2>
                <p style='color: #FAFAFA; margin: 1rem 0;'>
                    Get AI-powered insights, real-time market analysis, and personalized recommendations.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Main tabs with icons
        tabs = st.tabs(["📊 Analysis", "💹 Stocks", "📂 Portfolio"])

        with tabs[0]:
            st.header("Financial Analysis")

            # Query input card
            st.markdown("""
                <div style='margin-bottom: 1rem;'>
                    <p style='color: #FAFAFA;'>
                        Ask anything about finance, investments, or market trends.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            query = st.text_area(
                "What would you like to know?",
                placeholder="e.g., What are the best investment strategies for a recession?",
                height=100
            )

            # Analysis options
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
                                f"""<div style='
                                    background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
                                    padding: 2rem;
                                    border-radius: 12px;
                                    border-left: 5px solid #FF4B4B;
                                    margin-top: 1rem;
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                '>
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

            # Stock input section
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

                            # Candlestick chart
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
                                xaxis_rangeslider_visible=False,
                                margin=dict(t=100, b=50),
                                height=500
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # Key statistics in a modern card
                            st.markdown("### Key Statistics")
                            stats_cols = st.columns(4)
                            metrics = [
                                ("Open", df['1. open'].iloc[-1]),
                                ("Close", df['4. close'].iloc[-1]),
                                ("High", df['2. high'].iloc[-1]),
                                ("Low", df['3. low'].iloc[-1])
                            ]

                            for col, (label, value) in zip(stats_cols, metrics):
                                with col:
                                    st.metric(
                                        label,
                                        f"${value:.2f}",
                                        delta=f"{((value - df['1. open'].iloc[0]) / df['1. open'].iloc[0] * 100):.2f}%"
                                    )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with tabs[2]:
            st.header("Portfolio Analysis")

            # Portfolio input card
            st.markdown("""
                <div style='margin-bottom: 1rem;'>
                    <p style='color: #FAFAFA;'>
                        Enter your portfolio details and get personalized analysis.
                    </p>
                </div>
            """, unsafe_allow_html=True)

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
                                f"""<div style='
                                    background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
                                    padding: 2rem;
                                    border-radius: 12px;
                                    border-left: 5px solid #FF4B4B;
                                    margin-top: 1rem;
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                '>
                                    {result}
                                </div>""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Portfolio analysis failed")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

        # Footer
        st.markdown("""
            <div style='
                text-align: center;
                padding: 2rem;
                color: rgba(255,255,255,0.6);
                font-size: 0.8rem;
                margin-top: 2rem;
            '>
                <p>Smart Finance Analyzer | Built with 💜 using Streamlit</p>
                <p style='font-size: 0.7rem;'>
                    Disclaimer: This tool provides informational guidance only, not financial advice.
                    Consult with a certified financial advisor before making investment decisions.
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()