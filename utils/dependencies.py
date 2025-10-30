from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from functools import wraps

from models import User
from utils import get_db, Token


def get_current_user(request: Request, session: Session = Depends(get_db)):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing")

    # Expect header like "Bearer <token>"
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        access_token_payload = Token.verify_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    existing_user = session.query(User).filter(User.email == access_token_payload.get("email")).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return existing_user
