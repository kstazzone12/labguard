from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.qc.models import ControlIdentity, QcObservation


SYNTHETIC_CONTROL = ControlIdentity(
    material="Synthetic control material",
    lot="SYNTH-LOT-001",
    level="level-1",
    analyte="SYN-ANALYTE-01",
    method="SYN-METHOD-01",
    instrument="SYN-INSTRUMENT-01",
)


def build_levey_jennings_data() -> list[QcObservation]:
    mean = Decimal("100")
    standard_deviation = Decimal("2")
    values = ["99.8", "100.4", "101.0", "98.8", "100.2", "99.4", "100.8", "101.2", "99.6", "100.0"]
    start = datetime(2026, 1, 15, 8, 0, tzinfo=UTC)
    return [
        QcObservation(
            control=SYNTHETIC_CONTROL,
            run_number=index,
            timestamp=start + timedelta(minutes=index * 15),
            result=Decimal(value),
            mean=mean,
            standard_deviation=standard_deviation,
            operator="synthetic-operator",
        )
        for index, value in enumerate(values, start=1)
    ]
