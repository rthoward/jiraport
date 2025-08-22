"""Tests for issues.py functions."""

import pytest
import pendulum

from jiraport.issues import summarize, status_on, IssueSummary
from .factories import (
    IssueFactory,
    MockStatus,
    MockChangelog,
    MockHistory,
    MockHistoryItem,
)

DURATION_NONE = pendulum.Duration()
DT_CREATED = pendulum.datetime(2025, 1, 1)


class TestSummarize:
    def test_summarize_unstarted_issue(self):
        issue = IssueFactory(
            key="TEST-123",
            created=DT_CREATED.to_iso8601_string(),
            status=MockStatus("Done"),
        )

        assert summarize(issue) == IssueSummary(
            id="TEST-123",
            status="Done",
            story_points="",
            time_blocked=DURATION_NONE,
            time_dev=DURATION_NONE,
            date_created=DT_CREATED,
            date_in_dev=None,
            date_code_review=None,
            date_done=None,
        )

    def test_summarize_issue_with_development_history(self):
        issue = IssueFactory(
            key="TEST-456",
            created=DT_CREATED.to_iso8601_string(),
            status=MockStatus("Done"),
            changelog=MockChangelog(
                [
                    MockHistory(
                        created=DT_CREATED.add(days=2).to_iso8601_string(),
                        items=[MockHistoryItem("status", "To Do", "Development")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=5).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Development", "Code Review")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=6).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Development", "Done")],
                    ),
                ]
            ),
        )

        assert summarize(issue) == IssueSummary(
            id="TEST-456",
            status="Done",
            story_points="",
            date_created=DT_CREATED,
            date_in_dev=DT_CREATED.add(days=2),
            date_code_review=DT_CREATED.add(days=5),
            date_done=DT_CREATED.add(days=6),
            time_dev=pendulum.Duration(days=4),
            time_blocked=DURATION_NONE,
        )

    def test_summarize_blocked_issue(self):
        issue = IssueFactory(
            key="TEST-456",
            created=DT_CREATED.to_iso8601_string(),
            status=MockStatus("Done"),
            changelog=MockChangelog(
                [
                    MockHistory(
                        created=DT_CREATED.add(days=1).to_iso8601_string(),
                        items=[MockHistoryItem("status", "To Do", "Blocked")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=2).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Blocked", "Development")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=4).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Development", "Blocked")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=7).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Blocked", "Done")],
                    ),
                ]
            ),
        )

        assert summarize(issue) == IssueSummary(
            id="TEST-456",
            status="Done",
            story_points="",
            date_created=DT_CREATED,
            date_in_dev=DT_CREATED.add(days=2),
            date_code_review=None,
            date_done=DT_CREATED.add(days=7),
            time_dev=pendulum.Duration(days=2),
            time_blocked=pendulum.Duration(days=4),
        )


class TestStatusOn:
    @pytest.fixture
    def issue(self):
        return IssueFactory(
            key="TEST-456",
            created=DT_CREATED.to_iso8601_string(),
            status=MockStatus("Done"),
            changelog=MockChangelog(
                [
                    MockHistory(
                        created=DT_CREATED.add(days=1).to_iso8601_string(),
                        items=[MockHistoryItem("status", "To Do", "Blocked")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=2).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Blocked", "Development")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=4).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Development", "Blocked")],
                    ),
                    MockHistory(
                        created=DT_CREATED.add(days=7).to_iso8601_string(),
                        items=[MockHistoryItem("status", "Blocked", "Done")],
                    ),
                ]
            ),
        )

    def test_status_on_before_any_changes(self, issue):
        assert status_on(issue, DT_CREATED.subtract(days=10).date()) == "Created"
        assert status_on(issue, DT_CREATED.date()) == "Created"

    def test_status_after_blocked(self, issue):
        assert status_on(issue, DT_CREATED.add(days=1).date()) == "Blocked"

    def test_status_after_development(self, issue):
        assert status_on(issue, DT_CREATED.add(days=2).date()) == "Development"
        assert status_on(issue, DT_CREATED.add(days=3).date()) == "Development"

    def test_status_after_blocked_again(self, issue):
        assert status_on(issue, DT_CREATED.add(days=4).date()) == "Blocked"
        assert status_on(issue, DT_CREATED.add(days=5).date()) == "Blocked"
        assert status_on(issue, DT_CREATED.add(days=6).date()) == "Blocked"

    def test_status_after_done(self, issue):
        assert status_on(issue, DT_CREATED.add(days=7).date()) == "Done"
        assert status_on(issue, DT_CREATED.add(years=10).date()) == "Done"
