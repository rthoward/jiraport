import pytest
import vcr
from pendulum import DateTime, Duration

from jiraport.main import _jira_connect, DEFAULT_JQL
from jiraport import issues
from jiraport.utils import TZ


@pytest.mark.integration
@pytest.mark.vcr
def test_jira_integration(jira_config):
    jira_client = _jira_connect(**jira_config)

    jira_issues = jira_client.search_issues(
        DEFAULT_JQL,
        maxResults=5,
        expand="changelog",
        fields="id,created,status",
    )

    summaries = [issues.summarize(issue) for issue in jira_issues]

    assert summaries == [
        issues.IssueSummary(
            id="GCM-2237",
            status="Done",
            story_points="",
            time_blocked=Duration(),
            time_dev=Duration(days=1, minutes=44, seconds=49, microseconds=838000),
            date_created=DateTime(2025, 8, 19, 6, 56, 15, 157000, tzinfo=TZ),
            date_in_dev=DateTime(2025, 8, 19, 7, 0, 19, 550000, tzinfo=TZ),
            date_code_review=DateTime(2025, 8, 20, 7, 44, 26, 148000, tzinfo=TZ),
            date_done=DateTime(2025, 8, 20, 15, 44, 49, 52000, tzinfo=TZ),
        ),
        issues.IssueSummary(
            id="GCM-2082",
            status="Done",
            story_points="",
            time_blocked=Duration(),
            time_dev=Duration(
                days=3, hours=21, minutes=47, seconds=55, microseconds=262000
            ),
            date_created=DateTime(2025, 8, 13, 9, 3, 59, 971000, tzinfo=TZ),
            date_in_dev=DateTime(2025, 8, 14, 9, 0, 25, 497000, tzinfo=TZ),
            date_code_review=None,
            date_done=DateTime(2025, 8, 18, 6, 48, 20, 759000, tzinfo=TZ),
        ),
        issues.IssueSummary(
            id="GCM-2054",
            status="Done",
            story_points="",
            time_blocked=Duration(),
            time_dev=Duration(),
            date_created=DateTime(2025, 8, 12, 11, 44, 54, 246000, tzinfo=TZ),
            date_in_dev=None,
            date_code_review=None,
            date_done=DateTime(2025, 8, 18, 8, 47, 44, 51000, tzinfo=TZ),
        ),
        issues.IssueSummary(
            id="GCM-2053",
            status="Done",
            story_points="",
            time_blocked=Duration(),
            time_dev=Duration(hours=1, minutes=22, seconds=4, microseconds=54000),
            date_created=DateTime(2025, 8, 12, 11, 26, 34, 992000, tzinfo=TZ),
            date_in_dev=DateTime(2025, 8, 18, 7, 25, 36, 12000, tzinfo=TZ),
            date_code_review=DateTime(2025, 8, 18, 7, 25, 36, 12000, tzinfo=TZ),
            date_done=DateTime(2025, 8, 18, 8, 47, 40, 66000, tzinfo=TZ),
        ),
        issues.IssueSummary(
            id="GCM-2048",
            status="Done",
            story_points="",
            time_blocked=Duration(),
            time_dev=Duration(),
            date_created=DateTime(2025, 8, 12, 7, 24, 3, 268000, tzinfo=TZ),
            date_in_dev=None,
            date_code_review=None,
            date_done=DateTime(2025, 8, 13, 9, 0, 59, 137000, tzinfo=TZ),
        ),
    ]
