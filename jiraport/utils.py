from decimal import Decimal, ROUND_UP
from typing import Tuple
from typing_extensions import Optional, cast

import pendulum
from pendulum import Date, DateTime, Duration

TZ = pendulum.timezone("America/New_York")


def hr_date(dt: Optional[DateTime]):
    return dt.format("MM/DD/YYYY") if dt else ""


def half_days(dur: Duration) -> Decimal:
    if dur.total_seconds() < 1:
        return Decimal("0")

    days = Decimal(dur.total_days())
    half_days = (days * 2).quantize(Decimal("1"), rounding=ROUND_UP)
    days_rounded = (half_days / 2).quantize(Decimal("0.5"))
    return max(days_rounded, Decimal("0.5"))


def week_intervals(start_date: Date, end_date: Date) -> list[Tuple[Date, Date]]:
    interval_start = start_date.start_of("week")
    interval_end = start_date.end_of("week")
    intervals = []

    while interval_end <= end_date.end_of("week"):
        intervals.append((interval_start, interval_end))
        interval_start = interval_start.add(weeks=1)
        interval_end = interval_start.end_of("week")

    return intervals


def parse_dt(s: str) -> DateTime:
    dt = cast(DateTime, pendulum.parse(s))
    return TZ.convert(dt)


def parse_date(s: str) -> Date:
    return parse_dt(s).date()
