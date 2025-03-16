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

# Configure API URL for Replit environment
def get_api_url():
    """Get the correct API URL based on the environment"""
    base_url = "http://0.0.0.0:8000"
    return f"{base_url}/api"

API_URL = get_api_url()

def make_api_request(method, endpoint, data=None, json=None, timeout=5):
    """Make an API request with proper error handling"""
    try:
        url = f"{API_URL}/{endpoint}"
        kwargs = {
            'timeout': timeout,
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'}
        }
        if data:
            kwargs['data'] = data
        if json:
            kwargs['json'] = json
            kwargs['headers'] = {'Content-Type': 'application/json'}

        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Unable to connect to {url}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None

def login(username: str, password: str):
    """Authenticate user and store session data"""
    try:
        response = requests.post(
            f"{API_URL}/auth/token",
            data={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.username = data["username"]
            st.session_state.token = data["access_token"]
            return True
        return False
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the authentication server. Please try again.")
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def register(username: str, password: str):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            data={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            st.success("Registration successful! Please login.")
            return True
        else:
            error_detail = response.json().get("detail", "Registration failed")
            st.error(error_detail)
            return False
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the authentication server. Please try again.")
        return False
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return False

def create_strategy(strategy_data):
    """Create a new investment strategy"""
    try:
        response = make_api_request('post', 'strategies', json=strategy_data)
        if response and response.status_code == 200:
            st.success("Strategy created successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Failed to create strategy: {str(e)}")
        return False

def get_strategies():
    """Get list of investment strategies"""
    try:
        response = make_api_request('get', 'strategies')
        if response and response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Failed to fetch strategies: {str(e)}")
        return []

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

            tab1, tab2 = st.tabs(["Login", "Register"])

            with tab1:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Login")
                    if submitted:
                        if login(username, password):
                            st.success("Logged in successfully!")
                            st.rerun()

            with tab2:
                with st.form("register_form"):
                    new_username = st.text_input("Choose Username")
                    new_password = st.text_input("Choose Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    register_submitted = st.form_submit_button("Register")
                    if register_submitted:
                        if new_password != confirm_password:
                            st.error("Passwords do not match!")
                        else:
                            register(new_username, new_password)
        else:
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

        tabs = st.tabs(["📊 Analysis", "💹 Stocks", "📂 Portfolio", "🎯 Investment Strategies"])

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
                        response = make_api_request(
                            'post',
                            'analysis/analyze',
                            json={
                                "query_type": "generic",
                                "user_input": query,
                                "include_news": include_news,
                                "include_books": include_books
                            }
                        )
                        if response and response.status_code == 200:
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
                        response = make_api_request('get', f'analysis/stock/{symbol}')
                        if response and response.status_code == 200:
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
                        response = make_api_request(
                            'post',
                            'analysis/analyze',
                            json={
                                "query_type": "portfolio",
                                "user_input": query,
                                "portfolio_details": portfolio
                            }
                        )
                        if response and response.status_code == 200:
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

        with tabs[3]:
            st.header("Custom Investment Strategies")

            tab1, tab2 = st.tabs(["Create Strategy", "View Strategies"])

            with tab1:
                with st.form("create_strategy_form"):
                    st.subheader("Create New Strategy")

                    name = st.text_input("Strategy Name", placeholder="e.g., Conservative Growth Portfolio")
                    description = st.text_area("Strategy Description", 
                                             placeholder="Describe your investment strategy and goals",
                                             height=100)

                    col1, col2 = st.columns(2)
                    with col1:
                        risk_level = st.selectbox("Risk Level", 
                                                ["LOW", "MODERATE", "HIGH", "AGGRESSIVE"])
                        time_horizon = st.number_input("Time Horizon (months)", 
                                                     min_value=1, value=12)

                    with col2:
                        target_return = st.number_input("Target Annual Return (%)", 
                                                      min_value=0.0, value=10.0)
                        max_drawdown = st.number_input("Maximum Drawdown (%)", 
                                                     min_value=0.0, value=20.0)

                    investment_criteria = st.text_area("Investment Criteria",
                                                     placeholder="List your investment criteria and rules",
                                                     height=100)

                    submitted = st.form_submit_button("Create Strategy")
                    if submitted:
                        strategy_data = {
                            "name": name,
                            "description": description,
                            "risk_level": risk_level,
                            "time_horizon": time_horizon,
                            "investment_criteria": investment_criteria,
                            "target_return": target_return,
                            "max_drawdown": max_drawdown
                        }
                        create_strategy(strategy_data)

            with tab2:
                st.subheader("Your Investment Strategies")
                strategies = get_strategies()

                if strategies:
                    for strategy in strategies:
                        with st.expander(f"{strategy['name']} - {strategy['risk_level']}"):
                            st.markdown(f"**Description:** {strategy['description']}")
                            st.markdown(f"**Time Horizon:** {strategy['time_horizon']} months")
                            st.markdown(f"**Target Return:** {strategy['target_return']}%")
                            st.markdown(f"**Maximum Drawdown:** {strategy['max_drawdown']}%")
                            st.markdown(f"**Investment Criteria:**\n{strategy['investment_criteria']}")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Update Strategy", key=f"update_{strategy['id']}"):
                                    st.session_state.editing_strategy = strategy['id']
                            with col2:
                                if st.button("View Performance", key=f"performance_{strategy['id']}"):
                                    st.write("Performance metrics coming soon...")
                else:
                    st.info("No investment strategies found. Create your first strategy!")

if __name__ == "__main__":
    main()