from decimal import Decimal, ROUND_UP
from typing_extensions import Optional

import pendulum


def hr_date(dt: Optional[pendulum.DateTime]):
    return dt.format("MM/DD/YYYY") if dt else ""


def half_days(dur: pendulum.Duration) -> Decimal:
    if dur.total_seconds() < 1:
        return Decimal("0")

    days = Decimal(dur.total_days())
    half_days = (days * 2).quantize(Decimal("1"), rounding=ROUND_UP)
    days_rounded = (half_days / 2).quantize(Decimal("0.5"))
    return max(days_rounded, Decimal("0.5"))
