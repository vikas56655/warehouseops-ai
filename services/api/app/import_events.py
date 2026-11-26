import argparse
import csv

from sqlalchemy.orm import Session

from app.db import get_engine
from app.operations import Base, Event, ingest


def main():
    parser = argparse.ArgumentParser(description="Import validated warehouse events")
    parser.add_argument("csv_path")
    args = parser.parse_args()
    with open(args.csv_path, newline="", encoding="utf-8") as source:
        events = [Event.model_validate(row) for row in csv.DictReader(source)]
    engine = get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        print(f"Imported {ingest(session, events)} events")


if __name__ == "__main__":
    main()
