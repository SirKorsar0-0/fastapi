import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Імпортуємо Base та URL підключення з твого проекту
from app.database import Base, SQLALCHEMY_DATABASE_URL

# 2. ЯВНО імпортуємо класи моделей, щоб вони зареєструвалися в пам'яті Base.metadata
from app.models import User, Profile, Car, ServiceRecord, Part

# Об'єкт конфігурації Alembic
config = context.config

# Налаштовуємо логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаємо метадані твоїх моделей для автогенерації
target_metadata = Base.metadata

# Динамічно встановлюємо URL бази даних з нашого database.py
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Використовуємо актуальний config_ini_section замість застарілого config_sidecar
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаємо асинхронну функцію міграції
    asyncio.run(run_migrations_online())