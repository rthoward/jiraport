from dataclasses import dataclass
from typing import cast
from typing_extensions import Optional

from jira.resources import Issue
import pendulum


TZ = pendulum.timezone("America/New_York")
IN_DEV_STATUSES = {
    "Development",
    "Code Review",
    "Checked In",
    "QA",
    "Product Acceptance",
}


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

    for history in sorted(issue.changelog.histories, key=_created):
        status_items = [item for item in history.items if item.field == "status"]
        date_current = cast(pendulum.DateTime, pendulum.parse(history.created))
        date_current = TZ.convert(date_current)

        for item in status_items:
            # Track total blocked time.
            # For items entering a Blocked state, mark the time.
            # For items leaving a Blocked state, add the blocked duration to our total.
            if item.toString == "Blocked":
                date_blocked_start = date_current
            elif date_blocked_start and item.toString != "Blocked":
                time_blocked += date_current - date_blocked_start
                date_blocked_start = None

            # Track total in_dev time.
            if item.fromString in IN_DEV_STATUSES:
                time_dev += date_current - date_previous

            # Track the date of the first in_dev status.
            if item.toString in IN_DEV_STATUSES and date_in_dev is None:
                date_in_dev = date_current

            if item.toString == "Code Review":
                date_code_review = date_current

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


def _created(issue_history):
    return pendulum.parse(issue_history.created)
