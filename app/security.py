# app/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt

from app.database import get_db
from app.models import User
from app.config import settings  # Імпорт твого класу Settings

# Секретні налаштування динамічно тягнуться з BaseSettings конфігу
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Схема для авторизації в Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# === 1. ХЕШУВАННЯ ПАРОЛІВ (НАТИВНИЙ BCRYPT) ===

def get_password_hash(password: str) -> str:
    """Хешує чистий пароль за допомогою нативного bcrypt із генерацією солі"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє відповідність введеного пароля з хешем із бази даних"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


# === 2. ГЕНЕРАЦІЯ JWT ТОКЕНА ===

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Створює тимчасовий безпечний JWT токен для авторизованого користувача"""
    to_encode = data.copy()
    
    # Використовуємо modern часові пояси для сумісності з Python 3.12+
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# === 3. ЗАЛЕЖНІСТЬ (DEPENDENCY) ДЛЯ ЗАХИСТУ МАРШРУТІВ ===

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Автоматично витягує токен із заголовків запиту, валідує його та повертає поточного юзера"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити облікові дані (токен невалідний або застарів)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Асинхронний запит до бази даних для пошуку користувача
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    return user