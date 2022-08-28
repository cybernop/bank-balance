from typing import List

from account_check.statement_entry import StatementEntry


def sum_entries(entries: List[StatementEntry]) -> float:
    result = 0.0
    for entry in entries:
        result += entry.amount
    return result
