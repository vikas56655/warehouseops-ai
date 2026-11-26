from alembic import context

from app.db import get_engine
from app.operations import Base


def run():
    engine = get_engine()
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


run()
