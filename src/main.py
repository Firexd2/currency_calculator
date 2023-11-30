from typing import Annotated

from database import models
from database.engine import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.params import Query
from models import CalculatedRateResponse, ExchangeRate, ExchangeRateCreate
from sqlalchemy.orm import Session
from utils import build_graph, calculate_combined_rate, find_shortest_path

app = FastAPI()


CURRENCY_PAIR_ANNOTATION = Annotated[
    str, Query(min_length=3, max_length=7, regex="^[A-Z]{3}/[A-Z]{3}$", example="USD/EUR")
]
DATE_ANNOTATION = Annotated[
    str, Query(min_length=3, max_length=50, regex=r"^\d{4}\.\d{2}\.\d{2}$", example="2023.11.29")
]


@app.get("/exchange_rates/calculate", tags=["calculate"])
def calculate_exchange_rate(
    date: DATE_ANNOTATION, currency_pair: CURRENCY_PAIR_ANNOTATION, db: Session = Depends(get_db)
) -> CalculatedRateResponse:
    # first, try to find a direct rate
    direct_rate = (
        db.query(models.DailyExchangeRates)
        .filter(models.DailyExchangeRates.name == currency_pair, models.DailyExchangeRates.date == date)
        .first()
    )

    if direct_rate:
        return CalculatedRateResponse(date=direct_rate.date, name=direct_rate.name, rate=direct_rate.rate)

    # second, try to find a rate by back conversion
    # for example, if we have NZD/AUD, try to find AUD/NZD
    base_currency, target_currency = currency_pair.split("/")
    back_conversion_rate = (
        db.query(models.DailyExchangeRates)
        .filter(
            models.DailyExchangeRates.name == f"{target_currency}/{base_currency}",
            models.DailyExchangeRates.date == date,
        )
        .first()
    )

    if back_conversion_rate:
        return CalculatedRateResponse(
            date=back_conversion_rate.date, name=currency_pair, rate=1 / back_conversion_rate.rate
        )

    # get the most profitable rate using Dijkstra's algorithm
    all_rates = db.query(models.DailyExchangeRates).filter(models.DailyExchangeRates.date == date).all()
    graph = build_graph(all_rates)
    shortest_path = find_shortest_path(graph, base_currency, target_currency)
    if shortest_path:
        rate = calculate_combined_rate(shortest_path, graph)

        return CalculatedRateResponse(date=date, name=currency_pair, rate=rate)

    # if no rate can be calculated
    raise HTTPException(status_code=404, detail="Rate cannot be determined")


@app.get("/exchange_rates/history", tags=["history"])
def read_exchange_rate_history(
    currency_pair: CURRENCY_PAIR_ANNOTATION, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> list[ExchangeRate]:
    data = (
        db.query(models.DailyExchangeRates)
        .filter(models.DailyExchangeRates.name == currency_pair)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [ExchangeRate(id=rate.id, date=rate.date, name=rate.name, rate=rate.rate) for rate in data]


@app.post("/exchange_rates/", tags=["CRUD"])
def create_exchange_rate(rate: ExchangeRateCreate, db: Session = Depends(get_db)) -> ExchangeRate:
    db_rate = models.DailyExchangeRates(date=rate.date, name=rate.name, rate=rate.rate)
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)

    return ExchangeRate(id=db_rate.id, date=db_rate.date, name=db_rate.name, rate=db_rate.rate)


@app.get("/exchange_rates/", tags=["CRUD"])
def read_exchange_rates(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[ExchangeRate]:
    data = db.query(models.DailyExchangeRates).offset(skip).limit(limit).all()

    return [ExchangeRate(id=rate.id, date=rate.date, name=rate.name, rate=rate.rate) for rate in data]


@app.get("/exchange_rates/{rate_id}", tags=["CRUD"])
def read_exchange_rate(rate_id: int, db: Session = Depends(get_db)) -> ExchangeRate:
    db_rate = db.query(models.DailyExchangeRates).filter(models.DailyExchangeRates.id == rate_id).first()
    if db_rate is None:
        raise HTTPException(status_code=404, detail="Rate not found")

    return ExchangeRate(id=db_rate.id, date=db_rate.date, name=db_rate.name, rate=db_rate.rate)


@app.put("/exchange_rates/{rate_id}", tags=["CRUD"])
def update_exchange_rate(rate_id: int, rate: ExchangeRateCreate, db: Session = Depends(get_db)) -> ExchangeRate:
    db_rate = db.query(models.DailyExchangeRates).filter(models.DailyExchangeRates.id == rate_id).first()
    if db_rate is None:
        raise HTTPException(status_code=404, detail="Rate not found")
    db_rate.date = rate.date
    db_rate.name = rate.name
    db_rate.rate = rate.rate
    db.commit()
    db.refresh(db_rate)

    return ExchangeRate(id=db_rate.id, date=db_rate.date, name=db_rate.name, rate=db_rate.rate)


@app.delete("/exchange_rates/{rate_id}", tags=["CRUD"], status_code=204)
def delete_exchange_rate(rate_id: int, db: Session = Depends(get_db)) -> None:
    db_rate = db.query(models.DailyExchangeRates).filter(models.DailyExchangeRates.id == rate_id).first()
    if db_rate is None:
        raise HTTPException(status_code=404, detail="Rate not found")
    db.delete(db_rate)
    db.commit()
