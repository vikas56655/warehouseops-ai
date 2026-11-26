from fastapi import APIRouter, HTTPException
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_engine
from app.operations import summarize

router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


@router.get("/summary")
def summary():
    try:
        engine = get_engine()
        if not inspect(engine).has_table("operations"):
            return {"status": "not_initialized", "zones": []}
        with Session(engine) as session:
            return {"status": "ok", "zones": summarize(session)}
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Operations database unavailable") from exc
