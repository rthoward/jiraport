from dataclasses import dataclass
from enum import Enum
import os
from typing import cast
from typing_extensions import Optional

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
IN_PROGRESS_STATUSES = {"Development"}

JQL = """
type = Story AND labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND labels NOT IN (Cadent) AND status = Done AND project = GCM
"""

def main():
    j = JIRA(server=SERVER, basic_auth=(EMAIL, API_TOKEN))

    issues = j.search_issues(JQL, maxResults=1, expand="changelog")
    summaries = [summarize(issue) for issue in issues]

    print_table(summaries)


@dataclass
class IssueSummary:
    id: str
    status: str
    story_points: Optional[str]
    time_blocked: pendulum.Duration
    date_created: Optional[pendulum.DateTime]
    date_in_progress: Optional[pendulum.DateTime]
    date_code_review: Optional[pendulum.DateTime]
    date_done: Optional[pendulum.DateTime]


def summarize(issue: Issue) -> IssueSummary:
    date_created = cast(pendulum.DateTime, pendulum.parse(issue.fields.created))
    story_points = "todo"
    time_blocked = pendulum.Duration()
    blocked_start = None
    date_in_progress = None
    date_code_review = None
    date_done = None

    sort_key = lambda h: pendulum.parse(h.created)

    for history in sorted(issue.changelog.histories, key=sort_key):
        dt = cast(pendulum.DateTime, pendulum.parse(history.created))
        dt = TZ.convert(dt)

        for item in history.items:
            if item.field == "status":
                if blocked_start and item.toString != "Blocked":
                    time_blocked += (dt - blocked_start)
                    blocked_start = None
                elif item.toString == "Blocked":
                    blocked_start = dt

                if item.toString in IN_PROGRESS_STATUSES:
                    date_in_progress = dt
                elif item.toString == "Code Review":
                    date_code_review = dt
                elif item.toString == "Done":
                    date_done = dt

    return IssueSummary(
        id=issue.key,
        status=issue.fields.status.name,
        story_points=story_points,
        time_blocked=time_blocked,
        date_created=date_created,
        date_in_progress=date_in_progress,
        date_code_review=date_code_review,
        date_done=date_done,
    )


def to_csv_row(summary: IssueSummary):
    fields = [
        summary.id,
        summary.story_points,
        hr_date(summary.date_in_progress),
        hr_date(summary.date_code_review),
        hr_date(summary.date_done)
    ]

    return ",".join(fields)


def hr_date(dt: Optional[pendulum.DateTime]):
    return dt.format("MM/DD/YYYY") if dt else ""


def print_table(summaries: list[IssueSummary]):
    table = Table(title="Issue Summaries", expand=True)
    table.add_column("ID", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Story Points", no_wrap=True)
    table.add_column("Time Blocked", no_wrap=True)
    table.add_column("Created Date", no_wrap=True)
    table.add_column("In Progress Date", no_wrap=True)
    table.add_column("Code Review Date", no_wrap=True)
    table.add_column("Done Date", no_wrap=True)

    for summary in summaries:
        table.add_row(
            summary.id,
            summary.status,
            str(summary.story_points) if summary.story_points else "",
            str(summary.time_blocked) if summary.time_blocked else "",
            hr_date(summary.date_created),
            hr_date(summary.date_in_progress),
            hr_date(summary.date_code_review),
            hr_date(summary.date_done)
        )

    console = Console(width=120)
    console.print(table)


if __name__ == "__main__":
    main()
