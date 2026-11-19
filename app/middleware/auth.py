import datetime
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel


from app.config import get_settings


settings = get_settings()
security = HTTPBearer()
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


class User(BaseModel):
    username: str
    is_admin: bool = False
    
    
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_passowrd: str) -> bool:
    return pwd_context.verify(plain_password, hashed_passowrd)    


def create_access_token(username: str, delta: int | None = None, is_admin: bool = False) -> str:
    if delta is None:
        exp = settings.JWT_EXPIRATION_MINUTES * 60
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds = delta)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.datetime.now(datetime.UTC),
        "is_admin": is_admin
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm = "HS256")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms = ["HS256"])
        username = payload.get("sub")
        if not isinstance(username, str) or username is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid authentication error!"
                )
            is_admin: bool = payload.get("is_admin", False)
            return User(username = username, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token has expired",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token has expired"
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid authentication token",
        ) from None 


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Admin access required"
        )
    return user           
        
    