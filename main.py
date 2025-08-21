from dataclasses import dataclass
from enum import Enum
import os
from typing import cast
from typing_extensions import Optional

from jira import JIRA
from jira.resources import Issue, Status
import pendulum

EMAIL = os.environ["JIRA_EMAIL"]
API_TOKEN = os.environ["JIRA_TOKEN"]
SERVER = os.environ["JIRA_SERVER"]

TIMEZONE = pendulum.timezone("America/New_York")
ISSUE_FIELDS = "status,changelog"

JQL = """
type = Story AND labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND labels NOT IN (Cadent) AND status = Done AND project = GCM
"""

def transition_time(issue, from_status, to_status):
    ...


def main():
    j = JIRA(server=SERVER, basic_auth=(EMAIL, API_TOKEN))

    # issues = j.search_issues(JQL, maxResults=1, expand="changelog")
    # issue = issues[0]
    issue = j.issue("GCM-2082", expand="changelog", fields=ISSUE_FIELDS)
    summarize(issue)



# class Status(Enum):
#     DEVELOPMENT = "Development"
#     PRODUCT_ACCEPTANCE = "Product Acceptance"
#     DONE = "Done"


@dataclass
class IssueSummary:
    current_status: Status
    story_points: int
    time_blocked: Optional[pendulum.Duration]
    date_in_progress: Optional[pendulum.Date]
    date_code_review: Optional[pendulum.Date]
    date_done: Optional[pendulum.Date]


def summarize(issue: Issue) -> Optional[IssueSummary]:
    current_status: Status = issue.fields.status
    story_points: int
    time_blocked: Optional[pendulum.Duration]
    date_in_progress: Optional[pendulum.Date]
    date_code_review: Optional[pendulum.Date]
    date_done: Optional[pendulum.Date]

    sort_key = lambda h: pendulum.parse(h.created)

    for history in sorted(issue.changelog.histories, key=sort_key):
        dt = cast(pendulum.DateTime, pendulum.parse(history.created))

        for item in history.items:
            if item.field == "status":
                print(f"[{TIMEZONE.convert(dt)}] {item.fromString} -> {item.toString}")


if __name__ == "__main__":
    main()
