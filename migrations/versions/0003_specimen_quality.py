"""Add specimen quality and interference provenance fields.

Revision ID: 0003_specimen_quality
Revises: 0002_qc_fields
"""
from alembic import op
from sqlalchemy import Boolean, Column, DateTime, JSON, Numeric, String, Text, inspect

revision = "0003_specimen_quality"
down_revision = "0002_qc_fields"
branch_labels = None
depends_on = None

SAMPLE_COLUMNS = {
    "hemolysis_level": Column("hemolysis_level", String(50), nullable=True),
    "lipemia_level": Column("lipemia_level", String(50), nullable=True),
    "icteria_level": Column("icteria_level", String(50), nullable=True),
    "volume": Column("volume", Numeric(), nullable=True),
    "volume_unit": Column("volume_unit", String(50), nullable=True),
    "storage_condition": Column("storage_condition", String(200), nullable=True),
    "instrument_flags": Column("instrument_flags", JSON(), nullable=True),
}
INTERFERENCE_COLUMNS = {
    "manufacturer": Column("manufacturer", String(200), nullable=True),
    "level": Column("level", String(100), nullable=True),
    "criterion": Column("criterion", JSON(), nullable=True),
    "source_type": Column("source_type", String(50), nullable=True),
    "source_reference": Column("source_reference", Text(), nullable=True),
    "version": Column("version", String(50), nullable=True),
    "effective_date": Column("effective_date", DateTime(), nullable=True),
    "enabled": Column("enabled", Boolean(), nullable=True),
}


def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    with op.batch_alter_table("samples") as batch:
        existing = {column["name"] for column in inspector.get_columns("samples")}
        for name, column in SAMPLE_COLUMNS.items():
            if name not in existing:
                batch.add_column(column)
    with op.batch_alter_table("interferences") as batch:
        existing = {column["name"] for column in inspector.get_columns("interferences")}
        for name, column in INTERFERENCE_COLUMNS.items():
            if name not in existing:
                batch.add_column(column)


def downgrade() -> None:
    with op.batch_alter_table("interferences") as batch:
        for name in reversed(tuple(INTERFERENCE_COLUMNS)):
            batch.drop_column(name)
    with op.batch_alter_table("samples") as batch:
        for name in reversed(tuple(SAMPLE_COLUMNS)):
            batch.drop_column(name)
