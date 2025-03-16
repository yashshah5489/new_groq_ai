# rag_utils.py

import os
import logging
from dotenv import load_dotenv
from backend.news_fetcher import fetch_latest_news
from vector_store.chromadb_store import ChromaVectorStore

logger = logging.getLogger(__name__)
os.makedirs("logs", exist_ok=True)
load_dotenv()

# Instantiate the permanent vector store for self-help book learnings
self_help_vector_store = ChromaVectorStore(collection_name="self_help_books")

def get_latest_news_context(news_keywords, num_articles=5):
    """
    Fetch the latest news articles based on the provided news keywords.
    Returns a formatted string with the news articles.
    """
    try:
        news_articles = fetch_latest_news(query=news_keywords, num_articles=num_articles)
        if news_articles:
            context = "Latest News Articles:\n"
            if isinstance(news_articles, list):
                for article in news_articles:
                    context += f"- {article}\n"
            else:
                context += news_articles + "\n"
            return context
        else:
            return "No relevant news articles found.\n"
    except Exception as e:
        logger.error(f"Error fetching news articles: {e}")
        return "No news articles available.\n"

def retrieve_book_insights(query, n_results=3):
    """
    Retrieve self-help book insights from the permanent collection based on the query.
    Returns a formatted string with the insights.
    """
    try:
        insights = self_help_vector_store.query(query, n_results=n_results)
        if insights:
            context = "Self-Help Book Learnings:\n"
            if isinstance(insights, list):
                for insight in insights:
                    context += f"- {insight}\n"
            else:
                context += insights + "\n"
            return context
        else:
            return "No self-help book insights found.\n"
    except Exception as e:
        logger.error(f"Error retrieving book insights: {e}")
        return "No self-help book insights available.\n"

def get_rag_context(user_query, news_keywords):
    """
    Build a combined context string for RAG from the latest news and self-help book learnings.
    """
    news_context = get_latest_news_context(news_keywords) if news_keywords else "No news context provided.\n"
    book_context = retrieve_book_insights(user_query)
    combined_context = news_context + "\n" + book_context
    return combined_context
