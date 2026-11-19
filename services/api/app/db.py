from functools import lru_cache
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from app.config import settings

@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(settings.database_url, pool_pre_ping=True)

def check_database() -> bool:
    with get_engine().connect() as conn:
        return conn.execute(text("SELECT 1")).scalar_one() == 1
