from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from schema import UserSignupResponseSchema, UserSignupSchema, UserLoginSchema, RefreshTokenSchema
from utils import get_db, Token, PasswordHasher, get_current_user
from models import User, BlackListToken

user_router = APIRouter(prefix="/auth", tags=["Authentication"])


@user_router.post("/signup/", response_model=UserSignupResponseSchema)
def signup(user_detail: UserSignupSchema, session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.email == user_detail.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = PasswordHasher.hash_password(user_detail.password)
    new_user = User(
        email=user_detail.email,
        password=hashed_password,
        first_name=user_detail.first_name,
        last_name=user_detail.last_name,
    )

    session.add(new_user)
    session.commit()

    return JSONResponse(content={"message": "User created successfully"}, status_code=201)


@user_router.post("/login/")
def login(login_details: UserLoginSchema, session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.email == login_details.email).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Email or password is incorrect")

    password_status = PasswordHasher.verify_password(existing_user.password, login_details.password)
    if not password_status:
        raise HTTPException(status_code=400, detail="Email or password is incorrect")
    access_token, refresh_token = Token.generate_token(id=str(existing_user.id), email=existing_user.email)
    new_blacklist_token = BlackListToken(token=refresh_token)
    session.add(new_blacklist_token)
    session.commit()
    return JSONResponse(content={"message": "Login successful", "data": {
        "access_token": access_token,
        "refresh_token": refresh_token
    }}, status_code=200)


@user_router.post('/refresh-token')
def generate_token(token: RefreshTokenSchema, session: Session = Depends(get_db)):
    exisiting_token = session.query(BlackListToken).filter(BlackListToken.token == token.refresh_token).first()
    if not exisiting_token:
        raise HTTPException(status_code=400, detail="Token is invalid")
    user_details = Token.verify_refresh_token(token.refresh_token)
    existing_user = session.query(User).filter(
        User.email == user_details.get("email") and User.id == user_details.get("id")).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Token is invalid")
    access_token, refresh_token = Token.generate_token(id=str(existing_user.id), email=existing_user.email)
    new_blacklist_token = BlackListToken(token=refresh_token)
    session.add(new_blacklist_token)
    session.commit()
    return JSONResponse(content={"message": "Login successful", "data": {
        "access_token": access_token,
        "refresh_token": refresh_token
    }}, status_code=200)


@user_router.get("/me")
def get_user_details(user_details=Depends(get_current_user)):
    return JSONResponse({"data": {
        "email": user_details.email,
        "first_name": user_details.first_name,
        "last_name": user_details.last_name,
        "is_verified": user_details.is_verified,
        "created_at": user_details.created_at.isoformat()
    }})
