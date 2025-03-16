from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import jwt
from passlib.context import CryptContext
from database.database import get_db
from database.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get secrets from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Default for development
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == form_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Create new user with hashed password
        hashed_password = get_password_hash(form_data.password)
        user = User(
            username=form_data.username,
            hashed_password=hashed_password,
            email=form_data.username  # Using username as email for now
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "message": "User registered successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Find user by username
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
