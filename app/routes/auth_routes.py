from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token
from app.db.mongo_client import create_user, get_user_by_email, is_mongo_available

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest):
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB is not reachable. Set MONGODB_URI in .env to a running "
                   "instance (see docker-compose.yml) to enable auth/history.",
        )
    try:
        hashed = hash_password(payload.password)
        user_id = create_user(payload.email, hashed)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Database error: {e}")

    token = create_access_token(user_id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if not is_mongo_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB is not reachable. Set MONGODB_URI in .env to a running "
                   "instance (see docker-compose.yml) to enable auth/history.",
        )
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["hashedPassword"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(str(user["_id"]))
    return TokenResponse(access_token=token)
