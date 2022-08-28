from typing import List

from account_check.helpers import sum_entries
from account_check.statement_entry import StatementEntry


class Category:
    def __init__(self, entries: List[StatementEntry] = list()) -> None:
        self.entries = entries

    @property
    def total(self) -> float:
        return sum_entries(self.entries)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"total:{self.total}"
