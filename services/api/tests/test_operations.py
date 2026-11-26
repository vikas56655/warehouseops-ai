import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.operations import Base, Event, ingest, summarize


def event(**overrides):
    data = {"event_id": "e1", "occurred_at": "2026-01-01T08:00:00Z",
            "zone": "picking", "sku": "DEMO-1", "units": 10, "colis": 2,
            "duration_seconds": 60, "provenance": "synthetic_demo"}
    return Event.model_validate(dict(data, **overrides))


def test_import_and_summary():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        assert ingest(session, [event(), event(event_id="e2")]) == 2
        row = summarize(session)[0]
        assert row["units"] == 20
        assert row["units_per_hour"] == 600
        assert row["provenance"] == "synthetic_demo"


def test_invalid_event():
    with pytest.raises(ValidationError):
        event(duration_seconds=0)


def test_duplicate():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        ingest(session, [event()])
        with pytest.raises(ValueError):
            ingest(session, [event()])
        session.rollback()
        assert summarize(session)[0]["events"] == 1
