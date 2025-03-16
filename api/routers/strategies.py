from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database.database import get_db
from database.models import InvestmentStrategy, RiskLevel
from api.services.agent_manager import get_agent_advice

router = APIRouter()

class StrategyBase(BaseModel):
    name: str
    description: str
    risk_level: RiskLevel
    time_horizon: int
    investment_criteria: str
    target_return: float
    max_drawdown: float

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(StrategyBase):
    pass

class Strategy(StrategyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=Strategy, status_code=status.HTTP_201_CREATED)

async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    try:
        # Validate strategy with AI
        validation = get_agent_advice(
            "strategy_validation",
            user_input=f"Validate investment strategy: {strategy.dict()}"
        )
        
        db_strategy = InvestmentStrategy(**strategy.dict())
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        return db_strategy
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(InvestmentStrategy).filter(InvestmentStrategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(db_strategy)
    db.commit()

async def get_strategies(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    strategies = db.query(InvestmentStrategy).offset(skip).limit(limit).all()
    return strategies

@router.get("/user/{user_id}", response_model=List[Strategy])
async def get_strategies_by_user(user_id: int, db: Session = Depends(get_db)):
    strategies = db.query(InvestmentStrategy).filter(InvestmentStrategy.user_id == user_id).all()
    return strategies

async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = db.query(InvestmentStrategy).filter(InvestmentStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db)
):
    db_strategy = db.query(InvestmentStrategy).filter(InvestmentStrategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    for field, value in strategy_update.dict().items():
        setattr(db_strategy, field, value)
    
    try:
        db.commit()
        db.refresh(db_strategy)
        return db_strategy
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
