from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import config
engine = create_async_engine(
   f"postgresql+asyncpg://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}", 
    echo=False,
    pool_size=100)

async_session = sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()
