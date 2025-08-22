import pytest
from unittest.mock import Mock


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "serializer": "yaml",
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "once",
        "match_on": ["uri", "method"],
        "filter_headers": [
            "authorization",
            "x-atlassian-token",
        ],
        "filter_query_parameters": [
            "token",
            "key",
        ],
        "before_record_request": sanitize_request,
        "before_record_response": sanitize_response,
    }


def sanitize_request(request):
    if "authorization" in request.headers:
        request.headers["authorization"] = ["REDACTED"]
    return request


def sanitize_response(response):
    return response


@pytest.fixture
def mock_jira_client():
    mock_client = Mock()
    mock_client.search_issues.return_value = []
    return mock_client


@pytest.fixture
def jira_config():
    return {
        "server": "https://test.atlassian.net",
        "email": "test@example.com",
        "token": "test-token",
    }
