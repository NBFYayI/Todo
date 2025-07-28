from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.core.security import create_access_token, decode_access_token
from app.crud.user import get_user_by_email, create_user as crud_create_user, authenticate_user, get_user_by_id as crud_get_user_by_id, get_all_users as crud_get_all_users
from app.models.user import User

async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Register a new user and return the created User."""
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await crud_create_user(db, user_in)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> str:
    """Authenticate user and return a JWT access token."""
    user = await authenticate_user(db, email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(str(user.id))


async def get_user_from_token(db: AsyncSession, token: str) -> User:
    """Decode token and return the corresponding active user."""
    try:
        user_id = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_user_by_id_service(db: AsyncSession, user_id: int) -> User:
    """Get a user by ID."""
    user = await crud_get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def get_all_users_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination."""
    return await crud_get_all_users(db, skip=skip, limit=limit) 