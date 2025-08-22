import click
from jira import JIRA

from pendulum import Date

from jiraport import issues
from jiraport.click_utils import DateParamtype
from jiraport.output import print_table, write_csv
from jiraport.utils import week_intervals

DEFAULT_JQL = """
type = Story AND status = Done AND project = GCM AND
labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND
labels NOT IN (Cadent)
"""


@click.group()
@click.option(
    "--server",
    envvar="JIRA_SERVER",
    required=True,
    help="can also be set via JIRA_SERVER env var",
)
@click.option(
    "--email",
    envvar="JIRA_EMAIL",
    required=True,
    help="can also be set via JIRA_EMAIL env var",
)
@click.option(
    "--token",
    envvar="JIRA_TOKEN",
    required=True,
    help="can also be set via JIRA_TOKEN env var",
)
@click.pass_context
def cli(ctx, server, email, token):
    ctx.ensure_object(dict)
    ctx.obj["jira_config"] = {"server": server, "email": email, "token": token}


@cli.command()  # type: ignore
@click.option("--jql", default=DEFAULT_JQL.strip(), help="JQL query to execute")
@click.option(
    "--limit",
    type=int,
    help="Maximum number of issues to retrieve. Default: unlimited",
)
@click.option(
    "--output",
    "-o",
    multiple=True,
    default=["table", "csv"],
    help="Output format. Accepted: csv, table",
)
@click.pass_context
def summarize(ctx, jql, limit, output):
    """Summarize JIRA issues matching the given JQL query."""

    j = _jira_connect(**ctx.obj["jira_config"])

    click.echo("Searching with JQL:")
    click.echo(f"{jql}\n")

    limit = False if limit is None else limit
    jira_issues = j.search_issues(
        jql, maxResults=limit, expand="changelog", fields="id,created"
    )

    click.echo(f"Found {len(jira_issues)} issues. Summarizing...")
    summaries = [issues.summarize(issue) for issue in jira_issues]

    if "table" in output:
        print_table(summaries)

    if "csv" in output:
        write_csv(summaries)
        click.echo("CSV output written to output.csv")


@cli.command()
@click.argument("start_date", type=DateParamtype())
@click.argument("end_date", type=DateParamtype())
@click.pass_context
def weekly_load(ctx, start_date: Date, end_date: Date):
    j = _jira_connect(**ctx.obj["jira_config"])

    for i_start, i_end in week_intervals(start_date, end_date):
        jql = f"""
            project = GCM AND
            status CHANGED TO 'Development' during ({start_date}, {end_date})
        """

        jira_issues = j.search_issues(
            jql, maxResults=10, expand="changelog", fields="id,created"
        )

        for issue in jira_issues:
            print(issues.status_on(issue, i_start))


def _jira_connect(*, server, email, token) -> JIRA:
    click.echo("Connecting to JIRA server...", nl=False)
    j = JIRA(server=server, basic_auth=(email, token))
    click.echo("done.\n")

    return j


if __name__ == "__main__":
    cli()  # type: ignore
