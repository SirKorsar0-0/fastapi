from sqlalchemy import ForeignKey, String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Зв'язки
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    cars: Mapped[list["Car"]] = relationship("Car", back_populates="owner")

class Profile(Base):
    __tablename__ = "profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship("User", back_populates="profile")

class Car(Base):
    __tablename__ = "cars"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    vin: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship("User", back_populates="cars")
    records: Mapped[list["ServiceRecord"]] = relationship("ServiceRecord", back_populates="car")

class ServiceRecord(Base):
    __tablename__ = "service_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id", ondelete="CASCADE"))

    car: Mapped["Car"] = relationship("Car", back_populates="records")
    parts: Mapped[list["Part"]] = relationship("Part", back_populates="record")

class Part(Base):
    __tablename__ = "parts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    record_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_records.id", ondelete="CASCADE"))

    record: Mapped["ServiceRecord"] = relationship("ServiceRecord", back_populates="parts")