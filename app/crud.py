from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Profile, Car, ServiceRecord, Part
from app.schemas.user import UserCreate
from datetime import datetime
from app.auth import get_password_hash  

# === ЛАБА 5 (АВТЕНТИФІКАЦІЯ) ===
async def register_new_user(db: AsyncSession, user_data: UserCreate):
    secure_hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=secure_hashed_password, 
        age=user_data.age
    )
    db.add(db_user)
    await db.flush()
    
    db_profile = Profile(
        full_name=user_data.username,
        phone=None,
        user_id=db_user.id
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


# === ЛАБА 4 (СТАРІ CRUD ОПЕРАЦІЇ) ===
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data: dict, profile_data: dict):
    db_user = User(**user_data)
    db.add(db_user)
    await db.flush()
    db_profile = Profile(**profile_data, user_id=db_user.id)
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_cars_by_owner(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Car).filter(Car.owner_id == owner_id))
    return result.scalars().all()

async def create_car(db: AsyncSession, car_data: dict, owner_id: int):
    db_car = Car(**car_data, owner_id=owner_id)
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car


# === СІД БАЗИ ДАНИХ ===
async def seed_initial_data(db: AsyncSession):
    user_check = await db.execute(select(User))
    if user_check.scalars().first() is not None:
        return {"message": "База даних вже містить дані!"}

    user = User(
        email="denis.student@example.com",
        username="Denis_IT",
        hashed_password=get_password_hash("securejdm123"),
        age=18
    )
    db.add(user)
    await db.flush()

    profile = Profile(
        full_name="Denis",
        phone="+380991234567",
        user_id=user.id
    )
    db.add(profile)

    car1 = Car(brand="Nissan", model="Skyline GT-R R34", vin="BNR34-123456", owner_id=user.id)
    car2 = Car(brand="Mazda", model="MX-5 Miata", vin="NA6CE-654321", owner_id=user.id)
    db.add_all([car1, car2])
    await db.flush()

    record = ServiceRecord(
        description="Заміна масла в двигуні",
        mileage=120000,
        cost=4500.0,
        date=datetime.utcnow(),
        car_id=car1.id
    )
    db.add(record)
    await db.flush()

    part1 = Part(name="Моторне масло 5W-40", price=2500.0, record_id=record.id)
    db.add(part1)

    await db.commit()
    return {"message": "База даних успішно наповнена початковими даними!"}