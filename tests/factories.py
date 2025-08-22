from factory.base import Factory
from factory.declarations import LazyFunction, Sequence
from factory.helpers import lazy_attribute
from unittest.mock import Mock


from dataclasses import dataclass
from typing import List


@dataclass
class MockStatus:
    name: str


@dataclass
class MockHistoryItem:
    field: str
    fromString: str
    toString: str


@dataclass
class MockHistory:
    created: str
    items: List[MockHistoryItem]


@dataclass
class MockChangelog:
    histories: List[MockHistory]


class HistoryItemFactory(Factory):
    class Meta:  # type: ignore
        model = MockHistoryItem

    field = "status"
    fromString = "To Do"
    toString = "Development"


class HistoryFactory(Factory):
    class Meta:  # type: ignore
        model = MockHistory

    created = "2024-01-02T10:00:00.000+0000"
    items = LazyFunction(lambda: [HistoryItemFactory()])


class MockFields:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class IssueFactory(Factory):
    class Meta:  # type: ignore
        model = Mock

    key = Sequence(lambda n: f"TEST-{n}")

    _default_fields = {"status": "Created"}

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        issue_attrs = {"key", "changelog"}
        issue_kwargs = {k: v for k, v in kwargs.items() if k in issue_attrs}

        field_kwargs = {k: v for k, v in kwargs.items() if k not in issue_attrs}
        field_kwargs = {**cls._default_fields, **field_kwargs}
        fields = MockFields(**field_kwargs)

        return {**issue_kwargs, "fields": fields}

    @lazy_attribute
    def changelog(self):
        return MockChangelog([])
