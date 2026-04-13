from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.paths import DATABASE_URL
# from app.core.config import settings

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)