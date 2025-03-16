import os
import sys
import logging
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules
from backend.agent_manager import get_agent_advice
from vector_store.chromadb_store import ChromaVectorStore
# Import our RAG helper
from backend.rag_utils import get_rag_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# App configuration
st.set_page_config(
    layout="wide",
    page_title="Smart Finance Analyzer",
    page_icon=""
)

def main():
    try:
        st.title("Smart Finance Analyzer")

        # Instantiate the vector store for other document context (if needed)
        @st.cache_resource
        def get_vector_store():
            try:
                return ChromaVectorStore(collection_name="financial_docs")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                st.error("Could not connect to document database. Some features may be limited.")
                return None

        vector_store = get_vector_store()

        # Sidebar: Task selection and settings
        with st.sidebar:
            st.title("Navigation")
            # Simple authentication placeholder
            if 'authenticated' not in st.session_state:
                st.session_state.authenticated = False
            if not st.session_state.authenticated:
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Login"):
                    if username == "admin" and password == "password":
                        st.session_state.authenticated = True
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                        st.stop()
                st.stop()
            st.success("Logged in ✓")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()

            task_option = st.radio(
                "Select Task", 
                ["Generic Advice", "Portfolio Management", "Domain-Specific Advice"],
                help="All advice modules now incorporate latest news and self-help book learnings"
            )

            # News Keywords input for RAG context (applies to all modules)
            news_keywords = st.text_input(
                "News Keywords",
                placeholder="e.g. economy, motivation, recession",
                help="Keywords to fetch the latest news articles for context"
            )

            st.divider()
            st.markdown("### Advanced Settings")
            temperature = st.slider(
                "AI Creativity", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.7, 
                step=0.1,
                help="Higher values yield more creative responses but may be less accurate"
            )
            max_tokens = st.slider(
                "Response Length", 
                min_value=256, 
                max_value=4096, 
                value=1024, 
                step=256,
                help="Maximum length of the generated response"
            )

        # Main content: Tabs for advice input and history
        tab1, tab2 = st.tabs(["Get Advice", "History"])

        with tab1:
            if task_option == "Generic Advice":
                st.header("Generic Financial Advice")
                user_input = st.text_area(
                    "Describe your situation and the advice you need:",
                    placeholder="e.g. I'm 35 years old with 50,000 INR in savings. How should I invest for retirement?",
                    height=150
                )
                if st.button("Get Advice", key="generic", use_container_width=True):
                    if not user_input.strip():
                        st.error("Please enter your financial situation and question.")
                        st.stop()
                    with st.spinner("Generating personalized advice..."):
                        try:
                            # Build the combined RAG context using latest news and self-help insights
                            rag_context = get_rag_context(user_input, news_keywords)
                            answer = get_agent_advice(
                                "generic", 
                                context=rag_context, 
                                user_input=user_input,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            if 'history' not in st.session_state:
                                st.session_state.history = []
                            st.session_state.history.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "task": "Generic Advice",
                                "query": user_input,
                                "response": answer
                            })
                            st.subheader("Advice")
                            st.markdown(answer)
                        except Exception as e:
                            logger.error(f"Error generating advice: {e}")
                            st.error("An error occurred while generating advice. Please try again.")

            elif task_option == "Portfolio Management":
                st.header("Portfolio Management")
                with st.expander("Example Portfolio Format"):
                    st.code("""
Stocks: 40% (AAPL 10%, MSFT 8%, AMZN 7%, other tech 15%)
Bonds: 30% (Treasury 20%, Corporate 10%)
Real Estate: 20% (REITs)
Cash: 10%
Risk profile: Moderate
Investment horizon: 10 years
                    """)
                portfolio_details = st.text_area(
                    "Enter your portfolio details:",
                    placeholder="e.g. Stocks 60% (Tech 30%, Finance 20%, Healthcare 10%), Bonds 30%, Cash 10%",
                    height=150
                )
                user_input = st.text_area(
                    "What do you want to analyze?",
                    placeholder="e.g. Analyze my portfolio's risk profile for a recession scenario",
                    height=100
                )
                if st.button("Analyze Portfolio", key="portfolio", use_container_width=True):
                    if not portfolio_details.strip() or not user_input.strip():
                        st.error("Please enter both your portfolio details and query.")
                        st.stop()
                    with st.spinner("Analyzing portfolio..."):
                        try:
                            rag_context = get_rag_context(user_input, news_keywords)
                            answer = get_agent_advice(
                                "portfolio", 
                                portfolio_details=portfolio_details,
                                context=rag_context, 
                                user_input=user_input,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            if 'history' not in st.session_state:
                                st.session_state.history = []
                            st.session_state.history.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "task": "Portfolio Management",
                                "query": f"Portfolio: {portfolio_details}\nQuery: {user_input}",
                                "response": answer
                            })
                            st.subheader("Recommendations")
                            st.markdown(answer)
                        except Exception as e:
                            logger.error(f"Error analyzing portfolio: {e}")
                            st.error("An error occurred while analyzing your portfolio. Please try again.")

            elif task_option == "Domain-Specific Advice":
                st.header("Domain-Specific Investment Advice")
                domain_type = st.selectbox(
                    "Select Investment Domain",
                    ["Tech Stocks", "Cryptocurrency", "Real Estate", "Commodities", "ETFs & Mutual Funds", "Other"],
                    help="Choose the domain for advice"
                )
                domain_details = st.text_area(
                    f"Enter details of your {domain_type.lower()} holdings:",
                    placeholder="List your investments in this domain",
                    height=150
                )
                user_input = st.text_area(
                    "What advice do you need?",
                    placeholder="e.g. Should I rebalance my portfolio given recent market volatility?",
                    height=100
                )
                if st.button("Get Domain Advice", key="domain", use_container_width=True):
                    if not domain_details.strip() or not user_input.strip():
                        st.error("Please enter both your holdings and query.")
                        st.stop()
                    with st.spinner(f"Generating {domain_type} advice..."):
                        try:
                            domain_context = f"Investment Domain: {domain_type}\n\n{domain_details}"
                            rag_context = get_rag_context(user_input, news_keywords)
                            # You can combine domain_context with the rag_context if desired
                            full_context = domain_context + "\n\n" + rag_context
                            answer = get_agent_advice(
                                "domain", 
                                domain_details=domain_context,
                                context=full_context, 
                                user_input=user_input,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            if 'history' not in st.session_state:
                                st.session_state.history = []
                            st.session_state.history.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "task": f"Domain Advice: {domain_type}",
                                "query": f"Holdings: {domain_details}\nQuery: {user_input}",
                                "response": answer
                            })
                            st.subheader("Domain Recommendations")
                            st.markdown(answer)
                        except Exception as e:
                            logger.error(f"Error generating domain advice: {e}")
                            st.error("An error occurred while generating domain-specific advice. Please try again.")

        # History tab
        with tab2:
            st.header("Advice History")
            if 'history' not in st.session_state or not st.session_state.history:
                st.info("No advice history yet. Get some advice first!")
            else:
                for i, item in enumerate(reversed(st.session_state.history)):
                    with st.expander(f"{item['timestamp']} - {item['task']}"):
                        st.subheader("Your Query")
                        st.markdown(item["query"])
                        st.subheader("Response")
                        st.markdown(item["response"])
                        if st.button("Delete This Record", key=f"delete_{i}"):
                            original_idx = len(st.session_state.history) - 1 - i
                            st.session_state.history.pop(original_idx)
                            st.rerun()
                if st.button("Clear All History"):
                    st.session_state.history = []
                    st.rerun()

        # Footer
        st.divider()
        st.markdown(
            """
            <div style="text-align: center; color: gray; font-size: 0.8em;">
            Smart Finance Analyzer | Disclaimer: This tool provides informational guidance only, not financial advice.
            Consult with a certified financial advisor before making investment decisions.
            </div>
            """, 
            unsafe_allow_html=True
        )

    except Exception as e:
        logger.critical(f"Application error: {e}", exc_info=True)
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    main()