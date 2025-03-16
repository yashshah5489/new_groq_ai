from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import os
import uvicorn

# Import your existing functionality.
from backend.agent_manager import get_agent_advice
from backend.news_fetcher import fetch_latest_news
from vector_store.chromadb_store import ChromaVectorStore

# Ensure the logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ],
)

# Create logger
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Financial Analyzer API")

# Allow CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API data models
class AdviceRequest(BaseModel):
    task: str
    user_input: str
    additional_context_query: str = ""
    include_latest_news: bool = True
    portfolio_details: str = ""
    domain_details: str = ""
    domain_type: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024

class AdviceResponse(BaseModel):
    result: str

# Initialize vector store once
try:
    vector_store = ChromaVectorStore()
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    vector_store = None

@app.post("/api/analyze", response_model=AdviceResponse)
def analyze_advice(request: AdviceRequest):
    try:
        # Retrieve additional context from document and news sources if provided
        additional_context = ""
        if request.additional_context_query:
            doc_context = ""
            news_context = ""
            if vector_store:
                try:
                    docs = vector_store.query(request.additional_context_query, n_results=3)
                    if docs:
                        doc_context = "\n\n".join(docs)
                except Exception as e:
                    logger.error(f"Error retrieving documents: {e}")
            if request.include_latest_news:
                try:
                    news_context = fetch_latest_news(query=request.additional_context_query, num_articles=5)
                except Exception as e:
                    logger.error(f"Error fetching news: {e}")
            if doc_context:
                additional_context += f"Document Context:\n{doc_context}\n\n"
            if news_context:
                additional_context += f"Latest News:\n{news_context}"
        if not additional_context:
            additional_context = "No additional context provided."

        # Dispatch based on task type
        result = ""
        task = request.task.lower()
        if task == "generic":
            result = get_agent_advice(
                "generic", 
                context=additional_context, 
                user_input=request.user_input,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif task == "portfolio":
            result = get_agent_advice(
                "portfolio", 
                portfolio_details=request.portfolio_details,
                context=additional_context, 
                user_input=request.user_input,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif task == "domain":
            domain_context = f"Investment Domain: {request.domain_type}\n\n{request.domain_details}"
            result = get_agent_advice(
                "domain", 
                domain_details=domain_context,
                context=additional_context, 
                user_input=request.user_input,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid task type specified.")

        return AdviceResponse(result=result)
    except Exception as e:
        logger.error(f"Error generating advice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)