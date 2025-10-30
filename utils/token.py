from datetime import timedelta, datetime, timezone
from typing import Dict

from fastapi import HTTPException
from jwt import encode, decode, exceptions, ExpiredSignatureError, InvalidTokenError
from starlette import status

from const import ACCESS_SECRET_KEY, REFRESH_SECRET_KEY


class Token:

    @staticmethod
    def generate_token(email, id):
        access_token_payload = {
            "email": email,
            "id": id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        refresh_token_payload = {
            "email": email,
            "id": id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        access_token = encode(payload=access_token_payload, key=ACCESS_SECRET_KEY, algorithm='HS256')
        refresh_token = encode(payload=refresh_token_payload, key=REFRESH_SECRET_KEY, algorithm='HS256')
        return access_token, refresh_token

    @staticmethod
    def verify_access_token(access_token: str) -> str:
        try:
            payload = decode(access_token, ACCESS_SECRET_KEY, algorithms=['HS256'])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired",
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Access token",
            )

    @staticmethod
    def verify_refresh_token(refresh_token: str) -> Dict:
        try:
            payload = decode(refresh_token, REFRESH_SECRET_KEY, algorithms=['HS256'])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
