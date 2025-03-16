from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query = Column(Text)
    response = Column(Text)
    query_type = Column(String(50))  # generic, portfolio, domain
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskLevel(enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    AGGRESSIVE = "aggressive"

class InvestmentStrategy(Base):
    __tablename__ = "investment_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    risk_level = Column(Enum(RiskLevel))
    time_horizon = Column(Integer)  # In months
    investment_criteria = Column(Text)
    target_return = Column(Float)
    max_drawdown = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("investment_strategies.id"), index=True)
    date = Column(DateTime, index=True)
    return_rate = Column(Float)
    risk_metrics = Column(Text)  # JSON encoded risk metrics
    created_at = Column(DateTime, default=datetime.utcnow)