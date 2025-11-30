from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from sqlalchemy import and_, delete, or_
from sqlalchemy.orm import Session
from ..models import User, UserSession
from ..database import get_db
from ..security import generate_session_id, get_current_user, hash_password, verify_password, MAX_SESSION_AGE
from ..schemas import UserCreate, UserSchema

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


@router.post("/login", response_model=UserSchema)
def login_for_access_token(response: Response, username=Form(...), password = Form(...), db: Session = Depends(get_db)):
    user = get_user_from_db(db, username)
    if not user or not verify_password(password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = generate_session_id()
    # store the session
    newsession= UserSession(id=session_id, user_id=user.id)
    db.add(newsession)
    db.commit()
    db.refresh(newsession)
    # set the cookie
    max_age_seconds = int(MAX_SESSION_AGE.total_seconds())
    response.set_cookie(
        key="session_id",           # The name of the cookie
        value=session_id,           # The generated value
        httponly=True,              # Prevents JavaScript access (SECURITY BEST PRACTICE)
        secure=True,                # Ensures cookie is sent over HTTPS only (SECURITY BEST PRACTICE)
        samesite="lax",             # Mitigates CSRF attacks
        max_age=max_age_seconds,            # Optional: Cookie expiration time in seconds (e.g., 2 weeks)
        expires=max_age_seconds,            # Optional: Same as max_age, useful for older browsers
    )

    return user
@router.get("/logout")
def log_user_out(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    delete_stmt = delete(UserSession).where(and_(UserSession.id==session_id,UserSession.user_id == current_user.id))
    db.execute(delete_stmt)
    db.commit()
    # remove the cookie?

# Protected Endpoint Example
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    # The current_user object is now a SQLAlchemy model instance
    return {"username": current_user.username, "message": "You have access to protected data"}
