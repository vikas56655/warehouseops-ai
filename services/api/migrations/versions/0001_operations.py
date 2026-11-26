from alembic import op
import sqlalchemy as sa

revision = "0001_operations"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Existing Week 2 installations may already have this exact starter table.
    # Validate its structure before adopting it; never discard existing data.
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("operations"):
        columns = {c["name"] for c in inspector.get_columns("operations")}
        expected = {"event_id", "occurred_at", "zone", "sku", "units", "colis",
                    "duration_seconds", "provenance"}
        if columns != expected or inspector.get_pk_constraint("operations")[
            "constrained_columns"
        ] != ["event_id"]:
            raise RuntimeError("Existing operations schema requires manual review")
        return
    op.create_table(
        "operations",
        sa.Column("event_id", sa.String(100), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("zone", sa.String(20), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("colis", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("provenance", sa.String(30), nullable=False),
    )


def downgrade():
    raise RuntimeError("Destructive downgrade disabled; back up and migrate explicitly")
