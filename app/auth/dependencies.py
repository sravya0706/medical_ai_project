from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.auth.security import decode_access_token

bearer_scheme = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = credentials.credentials
    try:
        return decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
