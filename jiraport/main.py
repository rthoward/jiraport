import click
from jira import JIRA

from jiraport import issues
from jiraport.output import print_table, write_csv

DEFAULT_JQL = """
type = Story AND labels IN (G-DSP, G-SSP, G-Platform, G-Data) AND labels NOT IN (Cadent) AND status = Done AND project = GCM
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

    jira_config = ctx.obj["jira_config"]

    click.echo(f"Connecting to JIRA server: {jira_config['server']}")
    click.echo(f"Using JQL: {jql}")

    j = JIRA(
        server=jira_config["server"],
        basic_auth=(jira_config["email"], jira_config["token"]),
    )

    click.echo("Searching for issues...")
    limit = False if limit is None else limit
    jira_issues = j.search_issues(jql, maxResults=limit, expand="changelog")

    click.echo(f"Found {len(jira_issues)} issues. Summarizing...")
    summaries = [issues.summarize(issue) for issue in jira_issues]

    if "table" in output:
        print_table(summaries)

    if "csv" in output:
        write_csv(summaries)
        click.echo("CSV output written to output.csv")

if __name__ == "__main__":
    cli()  # type: ignore
