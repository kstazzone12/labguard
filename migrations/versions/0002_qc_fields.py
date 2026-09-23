"""Add QC run and result fields for the initial QC module.

Revision ID: 0002_qc_fields
Revises: 0001_initial
"""
from alembic import op
from sqlalchemy import Column, Integer, Numeric, String, inspect

revision = "0002_qc_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


QC_RUN_COLUMNS = {
    "control_material": Column("control_material", String(200), nullable=True),
    "run_number": Column("run_number", Integer(), nullable=True),
    "operator": Column("operator", String(100), nullable=True),
}
QC_RESULT_COLUMNS = {
    "result_value": Column("result_value", Numeric(), nullable=True),
    "mean": Column("mean", Numeric(), nullable=True),
    "standard_deviation": Column("standard_deviation", Numeric(), nullable=True),
    "cv_percent": Column("cv_percent", Numeric(), nullable=True),
    "z_score": Column("z_score", Numeric(), nullable=True),
    "sd_index": Column("sd_index", Numeric(), nullable=True),
    "position": Column("position", String(50), nullable=True),
}


def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    with op.batch_alter_table("qc_runs") as batch:
        existing = {column["name"] for column in inspector.get_columns("qc_runs")}
        for name, column in QC_RUN_COLUMNS.items():
            if name not in existing:
                batch.add_column(column)
    with op.batch_alter_table("qc_results") as batch:
        existing = {column["name"] for column in inspector.get_columns("qc_results")}
        for name, column in QC_RESULT_COLUMNS.items():
            if name not in existing:
                batch.add_column(column)


def downgrade() -> None:
    with op.batch_alter_table("qc_results") as batch:
        for name in reversed(tuple(QC_RESULT_COLUMNS)):
            batch.drop_column(name)
    with op.batch_alter_table("qc_runs") as batch:
        for name in reversed(tuple(QC_RUN_COLUMNS)):
            batch.drop_column(name)
