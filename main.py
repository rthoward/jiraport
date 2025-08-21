import click
from jira import JIRA

from jira_mine import issues
from jira_mine.output import print_table, write_csv

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
    "--max-results",
    type=int,
    help="Maximum number of results to return (default: no limit)",
)
@click.option(
    "--output",
    default="csv",
    help="Output format. Accepted: csv, table",
)
@click.pass_context
def summarize(ctx, jql, max_results, output):
    """Summarize JIRA issues matching the given JQL query."""

    jira_config = ctx.obj["jira_config"]

    click.echo(f"Connecting to JIRA server: {jira_config['server']}")
    click.echo(f"Using JQL: {jql}")

    j = JIRA(
        server=jira_config["server"],
        basic_auth=(jira_config["email"], jira_config["token"]),
    )

    click.echo("Searching for issues...")
    max_results = False if max_results is None else max_results
    jira_issues = j.search_issues(jql, maxResults=max_results, expand="changelog")

    click.echo(f"Found {len(jira_issues)} issues. Summarizing...")
    summaries = [issues.summarize(issue) for issue in jira_issues]

    if output == "table":
        print_table(summaries)
    elif output == "csv":
        write_csv(summaries)
        click.echo("CSV output written to output.csv")
    else:
        raise ValueError(f"Invalid output format: {output}")


if __name__ == "__main__":
    cli()  # type: ignore
