import requests
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from .utils import retry_with_backoff, rate_limit
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_ENDPOINT = "https://api.tavily.com/search"

# Create a cache to store news results
NEWS_CACHE: Dict[str, Dict] = {}
CACHE_EXPIRY = 3600  # Cache expires after 1 hour

logger = logging.getLogger(__name__)

@rate_limit(max_calls=20, period=60)  # Limit to 20 calls per minute
@retry_with_backoff(max_retries=3, initial_backoff=1, backoff_factor=2)
def fetch_latest_news(query: str = "", num_articles: int = 5, max_age_hours: int = 24) -> str:
    """
    Fetches the latest news articles from the Tavily API based on a query.
    
    Args:
        query: Search query for news
        num_articles: Number of articles to retrieve
        max_age_hours: Maximum age of articles in hours
        
    Returns:
        str: A formatted string combining headlines, sources, and descriptions
        
    Raises:
        ValueError: If API key is missing
        requests.RequestException: If there's an error with the request
    """
    if not query:
        query = "latest financial news market update"
        
    # Limit num_articles to a reasonable range
    num_articles = max(1, min(num_articles, 10))
    
    # Check cache first
    cache_key = f"{query}_{num_articles}_{max_age_hours}"
    if cache_key in NEWS_CACHE:
        cache_entry = NEWS_CACHE[cache_key]
        cache_time = cache_entry.get("timestamp")
        
        # If cache is still valid
        if cache_time and (datetime.now() - cache_time).total_seconds() < CACHE_EXPIRY:
            logger.info(f"Using cached news results for query: {query}")
            return cache_entry.get("news_context", "")
    
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    # Add financial context if query doesn't specify it
    if not any(term in query.lower() for term in ["finance", "market", "stock", "economic", "invest"]):
        search_query = f"{query} financial market implications"
    else:
        search_query = query
        
    # Calculate the date range for recent news
    current_time = datetime.now()
    start_date = (current_time - timedelta(hours=max_age_hours)).strftime("%Y-%m-%d")
    
    params = {
        "api_key": TAVILY_API_KEY,
        "query": search_query,
        "search_depth": "advanced",
        "include_domains": [
                "finance.yahoo.com",
                "bloomberg.com",
                "cnbc.com",
                "ft.com",
                "wsj.com",
                "reuters.com",
                "marketwatch.com",
                "economist.com",
                "barrons.com",
                "investing.com"
                ],
        "max_results": num_articles,
        "include_answer": True,
        "include_images": False,
        "include_raw_content": False,
        "start_date": start_date
    }
    
    try:
        logger.info(f"Fetching news for query: {search_query}")
        response = requests.post(
            TAVILY_API_ENDPOINT,
            json=params,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        if not result.get("results"):
            logger.warning(f"No news results found for query: {search_query}")
            return "No relevant financial news found."
            
        # Format the news articles
        formatted_news = []
        
        # Add AI-generated answer if available
        if result.get("answer"):
            formatted_news.append(f"### Summary\n{result['answer']}\n")
            
        # Add individual articles
        for i, article in enumerate(result.get("results", [])[:num_articles], 1):
            title = article.get("title", "Untitled")
            url = article.get("url", "")
            date = article.get("published_date", "")
            snippet = article.get("content", "")
            
            formatted_article = (
                f"#### {i}. {title}\n"
                f"**Source**: {url}\n"
                f"**Date**: {date}\n"
                f"{snippet}\n"
            )
            formatted_news.append(formatted_article)
            
        news_context = "\n".join(formatted_news)
        
        # Update cache
        NEWS_CACHE[cache_key] = {
            "timestamp": datetime.now(),
            "news_context": news_context
        }
        
        logger.info(f"Successfully fetched {len(result.get('results', []))} news articles")
        return news_context
        
    except requests.RequestException as e:
        logger.error(f"Error fetching news: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Tavily API error details: {json.dumps(error_detail)}")
            except:
                logger.error(f"Tavily API error status code: {e.response.status_code}")
        return f"Error fetching news: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching news: {str(e)}")
        return f"Unexpected error fetching news: {str(e)}"