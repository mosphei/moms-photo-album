from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..models import User
from ..database import get_db
from ..security import create_access_token, get_current_user, hash_password, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas import UserCreate, Token

router = APIRouter(
    prefix="/api/users",  # Sets the base path for all routes in this file
    tags=["users"],   # Groups these routes in the API docs (Swagger UI)
)

def get_user_from_db(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# User Registration Endpoint
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_from_db(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# Token Endpoint (Login)
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_from_db(db, form_data.username)
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Endpoint Example
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    # The current_user object is now a SQLAlchemy model instance
    return {"username": current_user.username, "message": "You have access to protected data"}
