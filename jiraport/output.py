import csv

from rich.console import Console
from rich.table import Table

from jiraport import issues
from jiraport.utils import half_days, hr_date


def print_table(summaries: list[issues.IssueSummary]):
    table = Table(title="Issue Summaries", expand=True)
    table.add_column("ID", no_wrap=True)
    table.add_column("Story Points", no_wrap=True)
    table.add_column("In Dev Date", no_wrap=True)
    table.add_column("Code Review Date", no_wrap=True)
    table.add_column("Done Date", no_wrap=True)
    table.add_column("Blocked?", no_wrap=True)
    table.add_column("Days Blocked", no_wrap=True)
    table.add_column("Days In Dev", no_wrap=True)
    table.add_column("Days In Dev + Blocked", no_wrap=True)

    for summary in summaries:
        table.add_row(
            summary.id,
            summary.story_points,
            hr_date(summary.date_in_dev),
            hr_date(summary.date_code_review),
            hr_date(summary.date_done),
            "Yes" if summary.time_blocked.total_seconds() > 0 else "No",
            str(half_days(summary.time_blocked)),
            str(half_days(summary.time_dev)),
            str(half_days(summary.time_dev) + half_days(summary.time_blocked)),
        )

    console = Console()

    # Hack for terminal multiplexers which often misrepresent terminal size.
    console.width = 240 if console.width == 80 else console.width

    console.print(table)


def write_csv(summaries: list[issues.IssueSummary]):
    rows = [to_csv_row(summary) for summary in summaries]
    fieldnames = rows[0].keys()

    with open("output.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_csv_row(summary: issues.IssueSummary):
    return {
        "ID": summary.id,
        "Story Points": summary.story_points,
        "Date In Dev": hr_date(summary.date_in_dev),
        "Date Code Review": hr_date(summary.date_code_review),
        "Date Done": hr_date(summary.date_done),
        "Blocked?": "Yes" if summary.time_blocked.total_seconds() > 0 else "No",
        "Days Blocked": str(half_days(summary.time_blocked)),
        "Days In Dev": str(half_days(summary.time_dev)),
        "Days In Dev + Blocked": half_days(summary.time_dev)
        + half_days(summary.time_blocked),
    }
