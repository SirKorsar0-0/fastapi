from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Імпортуємо генератор сесії бази даних (get_db)
from app.database import get_db
# Імпортуємо моделі
from app import models
# Імпортуємо схеми напряму з файлу user.py, щоб виправити AttributeError
from app.schemas import user as schemas

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 1. СТВОРЕННЯ КОРИСТУВАЧА (POST)
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Перевіряємо, чи немає вже користувача з такою поштою
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Користувач з таким Email вже зареєстрований!"
        )
    
    # Тимчасово робимо просте "хешування" для лабораторної
    fake_hashed_password = user_data.password + "notsecret"
    
    # Створюємо об'єкт моделі SQLAlchemy (так, як описано у вашому models.py)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        age=user_data.age,
        hashed_password=fake_hashed_password
    )
    
    # Зберігаємо у базу даних PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Повертає з бази згенерований ID
    
    return new_user


# 2. ОТРИМАННЯ ВСІХ КОРИСТУВАЧІВ (GET)
@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users