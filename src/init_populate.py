import csv
from datetime import UTC, datetime

import requests
from database.engine import get_postgres_engine
from database.models import DailyExchangeRates
from exceptions import TimeOutError
from sqlalchemy.orm import sessionmaker


def main() -> None:
    engine = get_postgres_engine()
    session = sessionmaker(bind=engine)()

    url = "https://drive.google.com/uc?id=1reh9OqlbqID0E314p--eYeElc7TEfLFM&export=download"

    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.Timeout as e:
        msg = "Timeout error"
        raise TimeOutError(msg) from e

    decoded_content = response.content.decode("utf-8")

    csv_reader = csv.reader(decoded_content.splitlines(), delimiter=",")
    _, *names = next(csv_reader)
    index_to_name = tuple((index, name) for index, name in enumerate(names, start=1))
    for row in csv_reader:
        date_ = row[0]
        date_ = datetime.strptime(date_, "%Y-%m-%d").replace(tzinfo=UTC)
        for index, name in index_to_name:
            rate = row[index]
            record = DailyExchangeRates(date=date_, name=name, rate=rate)
            session.add(record)

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
