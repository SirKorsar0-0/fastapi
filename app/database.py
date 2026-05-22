from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Зверніть увагу: ми використовуємо ім'я сервісу 'db' з вашого docker-compose.yml
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@db:5432/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()