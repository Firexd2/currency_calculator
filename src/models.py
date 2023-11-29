import re
from datetime import UTC, datetime

from _decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class CurrencyPair(str):

    @classmethod
    def validate(cls, value: str) -> str:
        if not bool(re.match(r"^[A-Z]{3}\/[A-Z]{3}$", value)):
            error = "Invalid currency pair format, expected BASE/TARGET"
            raise ValueError(error) from None

        return value

    def __get_pydantic_core_schema__(self) -> dict:
        return {
            "type": "str",
        }


class StringDate(str):

    @classmethod
    def validate(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y.%m.%d").replace(tzinfo=UTC)
        except ValueError:
            msg = "Invalid date format, expected YYYY.MM.DD"
            raise ValueError(msg) from None

        return value

    def __get_pydantic_core_schema__(self) -> dict:
        return {
            "type": "str",
        }


class ExchangeRateCreate(BaseModel):
    date: StringDate = Field(..., example="2023.11.29")
    name: CurrencyPair = Field(..., example="USD/EUR")
    rate: Decimal

    @field_validator("name")
    @classmethod
    def format_name(cls, value: CurrencyPair) -> CurrencyPair:
        CurrencyPair.validate(value)

        return value

    @field_validator("date")
    @classmethod
    def format_date(cls, value: StringDate) -> StringDate:
        StringDate.validate(value)

        return value


class ExchangeRate(BaseModel):
    id: int  # noqa: A003
    date: datetime | StringDate
    name: CurrencyPair
    rate: Decimal

    @field_validator("date")
    @classmethod
    def format_date(cls, value: datetime | StringDate) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y.%m.%d")

        return value

    @field_validator("name")
    @classmethod
    def format_name(cls, value: CurrencyPair) -> CurrencyPair:
        CurrencyPair.validate(value)

        return value

    class Config:
        from_attributes = True


class CalculatedRateResponse(BaseModel):
    date: datetime
    name: CurrencyPair
    rate: Decimal

    @field_validator("date")
    @classmethod
    def format_date(cls, value: datetime) -> str:
        return value.strftime("%Y.%m.%d")

    @field_validator("name")
    @classmethod
    def format_name(cls, value: CurrencyPair) -> CurrencyPair:
        CurrencyPair.validate(value)

        return value

    class Config:
        from_attributes = True
