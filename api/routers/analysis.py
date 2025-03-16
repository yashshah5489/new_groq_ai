from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from typing import Optional
from pydantic import BaseModel
from backend.agent_manager import get_agent_advice
from backend.news_fetcher import fetch_latest_news
from utils.stock_data import get_stock_data

router = APIRouter()

class AnalysisRequest(BaseModel):
    query_type: str
    user_input: str
    context: Optional[str] = None
    portfolio_details: Optional[str] = None
    domain_details: Optional[str] = None
    domain_type: Optional[str] = None

@router.post("/analyze")
async def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    try:
        # Get latest news for context
        news_context = fetch_latest_news(query=request.user_input)
        
        # Combine context
        full_context = f"{news_context}\n\n{request.context}" if request.context else news_context
        
        # Get analysis based on query type
        result = get_agent_advice(
            request.query_type,
            context=full_context,
            user_input=request.user_input,
            portfolio_details=request.portfolio_details,
            domain_details=request.domain_details
        )
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}")
async def get_stock_info(symbol: str):
    try:
        data = get_stock_data(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
