from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # Прибрали дублюючий імпорт select
from datetime import datetime
from typing import Optional, List

from app.models import User, Profile, Car, ServiceRecord, Part
from app.schemas.user import UserCreate
from app.security import get_password_hash

# === Користувачі ===

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

# ДОДАЛИ ФУНКЦІЮ, ЯКУ ШУКАВ РОУТЕР:
async def authenticate_user(db: AsyncSession, username: str) -> Optional[User]:
    """Шукає користувача в базі даних за його ім'ям для подальшої авторизації"""
    return await get_user_by_username(db, username)

async def register_new_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Реєстрація юзера + автоматичне створення профілю."""
    hashed_pwd = get_password_hash(user_data.password)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        age=user_data.age
    )
    db.add(new_user)
    await db.flush()  # Отримуємо ID юзера до коміту
    
    new_profile = Profile(full_name=user_data.username, user_id=new_user.id)
    db.add(new_profile)
    
    await db.commit()
    await db.refresh(new_user)
    return new_user

# === Автомобілі ===

async def get_cars_by_owner(db: AsyncSession, owner_id: int) -> List[Car]:
    result = await db.execute(select(Car).filter(Car.owner_id == owner_id))
    return result.scalars().all()

async def create_car(db: AsyncSession, car_data: dict, owner_id: int) -> Car:
    new_car = Car(**car_data, owner_id=owner_id)
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car

# === Сід бази (Database Seeding) ===

async def seed_initial_data(db: AsyncSession):
    """Наповнення бази тестовими даними."""
    try:
        # Перевірка чи є вже користувачі
        result = await db.execute(select(User).limit(1))
        if result.scalars().first():
            return {"message": "База вже має дані."}

        # Створення юзера
        user = User(
            email="denis.student@example.com",
            username="Denis_IT",
            hashed_password=get_password_hash("securejdm123"),
            age=18
        )
        db.add(user)
        await db.flush()

        # Профіль
        profile = Profile(full_name="Denis", phone="+380991234567", user_id=user.id)
        db.add(profile)

        # Автомобілі
        car1 = Car(brand="Nissan", model="Skyline GT-R R34", vin="BNR34-123456", owner_id=user.id)
        car2 = Car(brand="Mazda", model="MX-5 Miata", vin="NA6CE-654321", owner_id=user.id)
        db.add_all([car1, car2])
        await db.flush()

        # Запис сервісу
        record = ServiceRecord(
            description="Заміна масла",
            mileage=120000,
            cost=4500.0,
            date=datetime.now(),
            car_id=car1.id
        )
        db.add(record)
        await db.flush()

        # Деталі
        part = Part(name="Моторне масло 5W-40", price=2500.0, record_id=record.id)
        db.add(part)

        await db.commit()
        return {"message": "Дані успішно додано!"}
    
    except Exception as e:
        await db.rollback()
        return {"error": str(e)}