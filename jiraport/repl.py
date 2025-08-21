# ruff: noqa

import logging
import os

import IPython
from click import Context

from jiraport.main import _jira_connect


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    jira = _jira_connect(
        email=os.environ["JIRA_EMAIL"],
        server=os.environ["JIRA_SERVER"],
        token=os.environ["JIRA_TOKEN"],
    )
    IPython.embed()
