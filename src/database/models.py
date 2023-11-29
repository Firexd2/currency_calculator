from datetime import datetime

from psycopg2._psycopg import Decimal
from sqlalchemy import DECIMAL, TIMESTAMP, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class DBBase(DeclarativeBase):
    pass


class DailyExchangeRates(DBBase):
    __tablename__ = "daily_exchange_rates"
    id: int = Column(Integer, primary_key=True)  # noqa: A003

    date: datetime = Column(TIMESTAMP, nullable=False)
    name: str = Column(String(7), nullable=False)
    rate: Decimal = Column(DECIMAL, nullable=False)

    def __repr__(self) -> str:
        return f"DailyExchangeRates(id={self.id!r}, date={self.date!r})"
