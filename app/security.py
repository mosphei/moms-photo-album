from datetime import datetime, timedelta
import secrets
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from .models import User, UserSession
from .database import get_db
from pwdlib import PasswordHash

MAX_SESSION_AGE = timedelta(days=14)
password_hash = PasswordHash.recommended()

def generate_session_id(length_bytes=32):
    """
    Generates a secure, random session ID in hexadecimal format.
    
    The length_bytes parameter controls the entropy (randomness) of the token.
    32 bytes provides 256 bits of entropy, resulting in a 64 character hex string.
    """
    session_id = secrets.token_hex(length_bytes)
    return session_id

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    # first delete any expired sessions
    cutoff_time = datetime.utcnow() - MAX_SESSION_AGE
    delete_stmt = delete(UserSession).where(UserSession.timestamp < cutoff_time)
    db.execute(delete_stmt)
    db.commit()
    # cleanup_expired_sessions()
    sess = db.query(UserSession).filter(UserSession.id == session_id).first()
    user = None
    if sess:
        user = db.query(User).filter(User.id == sess.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate session",
        )
    return user

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

