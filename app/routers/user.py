from fastapi import APIRouter, Depends, HTTPException, status
from app import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app import models, auth
from app.schemas import user as schemas

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 1. СТВОРЕННЯ КОРИСТУВАЧА (POST)
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Перевірка, чи існує користувач за email
    existing_user = await crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Користувач з таким Email вже зареєстрований!"
        )
    
    # Хешуємо пароль перед збереженням
    hashed_password = auth.get_password_hash(user_data.password)
    
    # Створюємо користувача через CRUD
    new_user = await crud.create_user(db, user_data, hashed_password)
    return new_user

# 2. ОТРИМАННЯ ВСІХ КОРИСТУВАЧІВ (GET)
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    # Отримуємо всіх користувачів через CRUD
    users = await crud.get_all_users(db)
    return users