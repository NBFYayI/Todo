from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.services.user import register_user as service_register_user, login_user as service_login_user, get_user_from_token as service_get_user_from_token, get_user_by_id_service, get_all_users_service

router = APIRouter(prefix="/user", tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await service_register_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    access_token = await service_login_user(db, email=form_data.username, password=form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users", response_model=list[UserRead])
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all users with pagination."""
    users = await get_all_users_service(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a user by ID."""
    user = await get_user_by_id_service(db, user_id)
    return user 