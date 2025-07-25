# security.py
from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password) 

def create_access_token(sub: str) -> str:
    # 1) build an aware UTC datetime
    expire_dt = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # 2) extract the full-precision timestamp (a float, including microseconds)
    exp_timestamp = expire_dt.timestamp()

    to_encode = {
        "exp": exp_timestamp,   # pass the float explicitly
        "sub": sub,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    """Return the subject (user id) from a JWT token or raise."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    sub: str | None = payload.get("sub")
    if not sub:
        raise JWTError("Token missing subject")
    return sub

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Local import breaks the top‐level cycle
    from app.crud.user import get_user_by_id  

    credentials_exception = HTTPException(401, "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user
    