from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from . import schemas, models
from .database import get_db
from sqlalchemy.orm import Session
from typing import Optional

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


def get_password_hash(password: str) -> str:
    # 使用 pbkdf2_sha256，无需本地 bcrypt C 扩展，也没有 72 字节限制。
    if password is None:
        password = ""
    return pwd_context.hash(str(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password is None:
        plain_password = ""
    return pwd_context.verify(str(plain_password), hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    from jose import JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
