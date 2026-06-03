# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse, Token
from app import crud
import app.security as security_utils

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# === РЕЄСТРАЦІЯ ===
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Користувач з таким ім'ям вже існує"
        )
    return await crud.register_new_user(db, user_data)

# === ЛОГІН (З ДОДАВАННЯМ COOKIES ДЛЯ ЛАБИ 5) ===
@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # OAuth2PasswordRequestForm автоматично забирає username та password з форми (це стандарт FastAPI)
    user = await crud.authenticate_user(db, form_data.username)
    
    if not user or not security_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Створюємо JWT токен
    access_token = security_utils.create_access_token(data={"sub": user.username})
    
    # 🍪 ЗАПИСУЄМО ТОКЕН В COOKIES (Вимога куратора для Лаби 5)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return {"access_token": access_token, "token_type": "bearer"}

# === МІЙ ПРОФІЛЬ (ЗАХИЩЕНА РУЧКА) ===
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(security_utils.get_current_user)):
    return current_user