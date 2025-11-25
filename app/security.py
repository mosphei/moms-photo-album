from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt # Import the PyJWT library
from jwt import PyJWTError # Import the specific error class
# Assume get_user_from_db is imported from your database module
from database import get_db
from sqlalchemy.orm import Session
from models import User
from pwdlib import PasswordHash

# Secret key and algorithm for JWT (change these in a real application)
SECRET_KEY = "your-very-secure-and-long-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 15 # 15 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")
password_hash = PasswordHash.recommended()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=15)
    to_encode.update({"exp": expire})
    # Use jwt.encode from PyJWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    # Use the session to query the user
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

