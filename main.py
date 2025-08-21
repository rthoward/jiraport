import os

from jira import JIRA

from jira_mine import issues, output

EMAIL = os.environ["JIRA_EMAIL"]
API_TOKEN = os.environ["JIRA_TOKEN"]
SERVER = os.environ["JIRA_SERVER"]

ISSUE_FIELDS = "status,changelog,created"

JQL = """
type = Story AND labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND labels NOT IN (Cadent) AND status = Done AND project = GCM
"""


def main():
    j = JIRA(server=SERVER, basic_auth=(EMAIL, API_TOKEN))

    jira_issues = j.search_issues(JQL, maxResults=False, expand="changelog")
    summaries = [issues.summarize(issue) for issue in jira_issues]

    output.print_table(summaries)
    output.write_csv(summaries)


if __name__ == "__main__":
    main()
