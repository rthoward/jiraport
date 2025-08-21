import csv
from decimal import Decimal, ROUND_UP
from dataclasses import dataclass
import os
from typing import cast
from typing_extensions import Optional
import sys

from jira import JIRA
from jira.resources import Issue
import pendulum
from rich.console import Console
from rich.table import Table

EMAIL = os.environ["JIRA_EMAIL"]
API_TOKEN = os.environ["JIRA_TOKEN"]
SERVER = os.environ["JIRA_SERVER"]

TZ = pendulum.timezone("America/New_York")
ISSUE_FIELDS = "status,changelog,created"
IN_PROGRESS_STATUSES = {"Development", "Code Review", "Checked In", "QA", "Product Acceptance"}

JQL = """
type = Story AND labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND labels NOT IN (Cadent) AND status = Done AND project = GCM
"""

def main():
    j = JIRA(server=SERVER, basic_auth=(EMAIL, API_TOKEN))

    issues = j.search_issues(JQL, maxResults=False, expand="changelog")
    summaries = [summarize(issue) for issue in issues]

    print_table(summaries)
    write_csv(summaries)


@dataclass
class IssueSummary:
    id: str
    status: str
    story_points: Optional[str]

    time_blocked: pendulum.Duration
    time_dev: pendulum.Duration

    date_created: Optional[pendulum.DateTime]
    date_in_dev: Optional[pendulum.DateTime]
    date_code_review: Optional[pendulum.DateTime]
    date_done: Optional[pendulum.DateTime]


def summarize(issue: Issue) -> IssueSummary:
    story_points = ""
    time_blocked = pendulum.Duration()
    time_dev = pendulum.Duration()

    date_created = cast(pendulum.DateTime, pendulum.parse(issue.fields.created))
    date_previous = date_created
    date_blocked_start = None
    date_in_dev = None
    date_code_review = None
    date_done = None

    sort_key = lambda h: pendulum.parse(h.created)

    for history in sorted(issue.changelog.histories, key=sort_key):
        date_current = cast(pendulum.DateTime, pendulum.parse(history.created))
        date_current = TZ.convert(date_current)

        for item in history.items:
            if item.field == "status":
                if date_blocked_start and item.toString != "Blocked":
                    time_blocked += (date_current - date_blocked_start)
                    date_blocked_start = None
                elif item.toString == "Blocked":
                    date_blocked_start = date_current

                if item.fromString in IN_PROGRESS_STATUSES:
                    time_dev += (date_current - date_previous)

                if item.toString == "Code Review":
                    date_code_review = date_current

                if item.toString in IN_PROGRESS_STATUSES and date_in_dev is None:
                    date_in_dev = date_current

                if item.toString == "Done":
                    date_done = date_current

        date_previous = date_current


    return IssueSummary(
        id=issue.key,
        status=issue.fields.status.name,
        story_points=story_points,
        time_blocked=time_blocked,
        time_dev=time_dev,
        date_created=date_created,
        date_in_dev=date_in_dev,
        date_code_review=date_code_review,
        date_done=date_done,
    )


def hr_date(dt: Optional[pendulum.DateTime]):
    return dt.format("MM/DD/YYYY") if dt else ""


def half_days(dur: pendulum.Duration) -> Decimal:
    if dur.total_seconds() < 1:
        return Decimal("0")

    days = Decimal(dur.total_days())
    half_days = (days * 2).quantize(Decimal("1"), rounding=ROUND_UP)
    days_rounded = (half_days / 2).quantize(Decimal("0.5"))
    return max(days_rounded, Decimal("0.5"))


def print_table(summaries: list[IssueSummary]):
    table = Table(title="Issue Summaries", expand=True)
    table.add_column("ID", no_wrap=True)
    table.add_column("Story Points", no_wrap=True)
    table.add_column("In Dev Date", no_wrap=True)
    table.add_column("Code Review Date", no_wrap=True)
    table.add_column("Done Date", no_wrap=True)
    table.add_column("Blocked?", no_wrap=True)
    table.add_column("Days Blocked", no_wrap=True)
    table.add_column("Days In Dev", no_wrap=True)
    table.add_column("Days In Dev + Blocked", no_wrap=True)

    for summary in summaries:
        table.add_row(
            summary.id,
            summary.story_points,
            hr_date(summary.date_in_dev),
            hr_date(summary.date_code_review),
            hr_date(summary.date_done),
            "Yes" if summary.time_blocked.total_seconds() > 0 else "No",
            str(half_days(summary.time_blocked)),
            str(half_days(summary.time_dev)),
            str(half_days(summary.time_dev) + half_days(summary.time_blocked))
        )

    console = Console(width=240)
    console.print(table)


def write_csv(summaries: list[IssueSummary]):
    rows = [to_csv_row(summary) for summary in summaries]
    fieldnames = rows[0].keys()

    with open("output.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_csv_row(summary: IssueSummary):
    return {
        "ID": summary.id,
        "Story Points": summary.story_points,
        "Date In Dev": hr_date(summary.date_in_dev),
        "Date Code Review": hr_date(summary.date_code_review),
        "Date Done": hr_date(summary.date_done),
        "Blocked?": "Yes" if summary.time_blocked.total_seconds() > 0 else "No",
        "Days Blocked": str(half_days(summary.time_blocked)),
        "Days In Dev": str(half_days(summary.time_dev)),
        "Days In Dev + Blocked": half_days(summary.time_dev) + half_days(summary.time_blocked),
    }


if __name__ == "__main__":
    main()
