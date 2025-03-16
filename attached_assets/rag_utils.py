# rag_utils.py

import os
import logging
from dotenv import load_dotenv
from backend.news_fetcher import fetch_latest_news
from vector_store.chromadb_store import ChromaVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)
os.makedirs("logs", exist_ok=True)
load_dotenv()

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

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
            # Split news articles into chunks for better context
            if isinstance(news_articles, list):
                chunks = []
                for article in news_articles:
                    article_chunks = text_splitter.split_text(article)
                    chunks.extend(article_chunks)
            else:
                chunks = text_splitter.split_text(news_articles)

            context = "Latest News Articles:\n"
            for chunk in chunks:
                context += f"- {chunk}\n"
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
        # Split query into smaller chunks for better matching
        query_chunks = text_splitter.split_text(query)
        all_insights = []

        # Query for each chunk and combine results
        for chunk in query_chunks:
            insights = self_help_vector_store.query(chunk, n_results=n_results)
            if insights and isinstance(insights, list):
                all_insights.extend(insights)

        # Remove duplicates and format
        unique_insights = list(set(all_insights))
        if unique_insights:
            context = "Self-Help Book Learnings:\n"
            for insight in unique_insights[:n_results]:  # Limit to n_results
                context += f"- {insight}\n"
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

    # Log retrieval results
    logger.info(f"Retrieved news context length: {len(news_context)}")
    logger.info(f"Retrieved book insights length: {len(book_context)}")

    combined_context = news_context + "\n" + book_context
    return combined_context