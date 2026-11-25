from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.db.models import UserDB
from app.db.session import SessionDep
from app.middleware.auth import create_access_token, hash_password, verify_password
from app.middleware.rate_limiter import is_allowed_ip

router = APIRouter(tags = ["auth"])
settings = get_settings()


@router.post("/auth/register", status_code = status.HTTP_201_CREATED)
async def register(request: Request, body: dict, session: SessionDep) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    allowed, _, _ = is_allowed_ip(
        client_ip,
        "/auth/register",
        limit = settings.AUTH_REGISTER_RATE_LIMIT_PER_HOUR,
        window_seconds = 3600,
    )
    if not allowed:
        raise HTTPException(status_code = 429, detail = "Rate limit exceeded")

    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        raise HTTPException(status_code = 400, detail = "username and password required")

    new_user = UserDB(
        username = username,
        password_hash = hash_password(password),
    )

    try:
        session.add(new_user)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code = 409, detail = "User already exists") from None

    token = create_access_token(new_user.username)
    return {"token": token}


@router.post("/auth/login")
async def login(request: Request, body: dict, session: SessionDep) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    allowed, _, _ = is_allowed_ip(
        client_ip,
        "/auth/login",
        limit = settings.AUTH_LOGIN_RATE_LIMIT_PER_MIN,
        window_seconds = 60,
    )
    if not allowed:
        raise HTTPException(status_code = 429, detail = "Rate limit exceeded")

    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        raise HTTPException(status_code = 400, detail = "username and password required")

    stmt = select(UserDB).where(UserDB.username == username)
    user = await session.scalar(stmt)

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code = 401, detail = "Invalid credentials")

    token = create_access_token(user.username, is_admin = user.is_admin)
    return {"token": token}