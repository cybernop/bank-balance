from typing import List

from account_check.helpers import sum_entries
from account_check.statement_entry import StatementEntry


class Category:
    def __init__(self, name: str, entries: List[StatementEntry] = None) -> None:
        self.name = name
        self.entries = entries if entries else list()
        self.relative_total = 0.0

    def append(self, value: StatementEntry) -> None:
        self.entries.append(value)

    @property
    def amount(self) -> float:
        return sum_entries(self.entries)

    @property
    def relative(self) -> float:
        return self.amount / self.relative_total

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.name}: {self.amount}"
