# rag_advice_with_books.py

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import your vector store class from your repository
from vector_store.chromadb_store import ChromaVectorStore
# Import your news fetcher function
from backend.news_fetcher import fetch_latest_news
# Import the Groq client from the groq package
from groq import Groq

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
os.makedirs("logs", exist_ok=True)

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY is not set!")
    exit(1)

# Initialize the Groq LLM client per the quickstart guide
llm_client = Groq(api_key=GROQ_API_KEY)

# Initialize two vector stores:
# One for self-help book insights and one for financial docs (if needed)
self_help_vector_store = ChromaVectorStore(collection_name="self_help_books")
financial_vector_store = ChromaVectorStore(collection_name="financial_docs")

# =============================================================================
# SECTION 1: ADDING SELF-HELP BOOK INSIGHTS TO CHROMADB
# =============================================================================

def add_self_help_book_insights(insights):
    """
    Add a list of self-help book insights to the ChromaDB collection.
    Each insight is vectorized automatically by ChromaDB.
    """
    if not insights:
        logger.warning("No insights provided to add.")
        return

    # Generate unique IDs for each insight
    ids = [f"book_insight_{i+1}" for i in range(len(insights))]
    # Metadata to indicate the source
    metadatas = [{"source": "self_help_book"} for _ in insights]
    
    try:
        self_help_vector_store.add_documents(ids, insights, metadatas)
        logger.info("Self-help book insights added successfully!")
    except Exception as e:
        logger.error(f"Error adding self-help book insights: {e}")

# Example usage (run once to add insights):
insights_list = [
    "Embrace failure as a learning opportunity and step toward success.",
    "Daily mindfulness practices improve focus and reduce stress.",
    "Clarity of purpose fuels consistent progress."
]
add_self_help_book_insights(insights_list)

# =============================================================================
# SECTION 2: RETRIEVAL-ENHANCED GENERATION (RAG) FUNCTIONALITY
# =============================================================================

def build_rag_prompt(user_query, news_articles, book_insights):
    """
    Build a combined prompt from news articles, self-help insights, and the user query.
    """
    prompt = (
        "You are a seasoned financial advisor with access to both the latest news and "
        "timeless self-help wisdom. Provide a comprehensive answer to the following query.\n\n"
    )
    if news_articles:
        prompt += "Latest News Articles:\n"
        for article in news_articles:
            prompt += f"- {article}\n"
    else:
        prompt += "No relevant news articles found.\n"
    if book_insights:
        prompt += "\nSelf-Help Book Insights:\n"
        for insight in book_insights:
            prompt += f"- {insight}\n"
    else:
        prompt += "\nNo self-help book insights available.\n"
    prompt += "\nUser Query:\n" + user_query + "\n\nAnswer:"
    return prompt

def log_prompt(prompt, file_path="logs/groq_prompt.txt"):
    """
    Append the full prompt with a timestamp to a log file.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(prompt + "\n" + ("-" * 80) + "\n")
    except Exception as e:
        logger.error(f"Error logging prompt: {e}")

def retrieve_book_insights(query, n_results=3):
    """
    Retrieve self-help book insights relevant to the given query.
    """
    try:
        insights = self_help_vector_store.query(query, n_results=n_results)
        return insights
    except Exception as e:
        logger.error(f"Error retrieving self-help insights: {e}")
        return []

def get_rag_advice(user_query, news_keywords=None, temperature=0.7, max_tokens=1024):
    """
    Generate advice using RAG by combining the latest news and self-help book insights.
    
    Parameters:
      user_query (str): The user's query.
      news_keywords (str): Keywords to fetch the latest news articles.
      temperature (float): LLM creativity parameter.
      max_tokens (int): Maximum token count for the response.
    
    Returns:
      The response from the Groq LLM.
    """
    # Fetch latest news articles using the provided keywords (if any)
    news_articles = []
    if news_keywords:
        try:
            news_articles = fetch_latest_news(query=news_keywords, num_articles=5)
        except Exception as e:
            logger.error(f"Error fetching news articles: {e}")
    
    # Retrieve self-help book insights related to the query
    book_insights = retrieve_book_insights(user_query, n_results=3)
    
    # Build the combined prompt
    prompt = build_rag_prompt(user_query, news_articles, book_insights)
    
    # Log the prompt for future reference
    log_prompt(prompt)
    
    logger.info("Prompt being sent to Groq LLM:")
    logger.info(prompt)
    
    try:
        # Prepare chat messages as required by the Groq Chat API
        messages = [
            {"role": "system", "content": "You are a seasoned financial advisor with access to both the latest news and timeless self-help wisdom."},
            {"role": "user", "content": prompt}
        ]
        # Call the Groq API using the correct method per the quickstart:
        chat_completion = llm_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=temperature
        )
        # Extract and return the answer from the response
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return None

# =============================================================================
# SECTION 3: MAIN FUNCTION (For Testing/Integration)
# =============================================================================

def main():
    # For demonstration purposes, define a sample user query and news keywords.
    user_query = "How can I stay motivated during tough economic times?"
    news_keywords = "economy, motivation, recession"
    
    # Optionally, run this once to add self-help insights (uncomment to load them into ChromaDB)
    sample_insights = [
        "Embrace failure as a learning opportunity and step toward success.",
        "Daily mindfulness practices improve focus and reduce stress.",
        "Clarity of purpose fuels consistent progress."
    ]
    add_self_help_book_insights(sample_insights)
    
    # Generate advice using RAG
    advice_response = get_rag_advice(user_query, news_keywords=news_keywords)
    if advice_response:
        print("RAG Advice Response:\n", advice_response)
    else:
        print("No response received.")

if __name__ == "__main__":
    main()
