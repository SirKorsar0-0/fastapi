from pydantic import BaseModel, Field
from typing import Optional

# Схема для реєстрації нового користувача (те, що надсилає клієнт)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str  # Змінили з EmailStr на str, щоб не вимагати додаткових пакетів
    age: Optional[int] = Field(None, ge=18, le=100)
    password: str = Field(..., min_length=8)

# Схема для відповіді клієнту (те, що ми повертаємо назад)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int] = None

    class Config:
        from_attributes = True  # Дозволяє зчитувати дані з моделей SQLAlchemy

# Схема для входу (те, що надсилає клієнт при логіні)
class UserLogin(BaseModel):
    username: str
    password: str

# Схема для повернення JWT токена клієнту
class Token(BaseModel):
    access_token: str
    token_type: str