from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Operation(Base):
    __tablename__ = "operations"
    event_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    zone: Mapped[str] = mapped_column(String(20))
    sku: Mapped[str] = mapped_column(String(100))
    units: Mapped[int] = mapped_column(Integer)
    colis: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    provenance: Mapped[str] = mapped_column(String(30))


class Event(BaseModel):
    event_id: str = Field(min_length=1, max_length=100)
    occurred_at: AwareDatetime
    zone: Literal["reception", "picking", "storage", "dispatch"]
    sku: str = Field(min_length=1, max_length=100)
    units: int = Field(ge=1)
    colis: int = Field(ge=0)
    duration_seconds: int = Field(gt=0)
    provenance: Literal["synthetic_demo", "public_dataset"]


def ingest(session: Session, events: list[Event]) -> int:
    seen = set()
    inserted = 0
    for event in events:
        if event.event_id in seen:
            raise ValueError(f"Duplicate event ID: {event.event_id}")
        seen.add(event.event_id)
        existing = session.get(Operation, event.event_id)
        if existing is not None:
            raise ValueError(f"Event already exists: {event.event_id}")
        session.add(Operation(**event.model_dump()))
        inserted += 1
    session.commit()
    return inserted


def summarize(session: Session) -> list[dict]:
    totals = {}
    for event in session.scalars(select(Operation)):
        key = (event.zone, event.provenance)
        row = totals.setdefault(key, {"zone": event.zone, "provenance": event.provenance,
                                     "events": 0, "units": 0, "colis": 0, "seconds": 0})
        row["events"] += 1
        row["units"] += event.units
        row["colis"] += event.colis
        row["seconds"] += event.duration_seconds
    return [dict(row, units_per_hour=round(row["units"] * 3600 / row["seconds"], 2))
            for _, row in sorted(totals.items())]
