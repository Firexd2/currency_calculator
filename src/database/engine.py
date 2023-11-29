from config import settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker


def get_postgres_engine() -> Engine:
    return create_engine(settings.POSTGRES_URI)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_postgres_engine())


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
