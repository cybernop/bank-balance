from typing import List

from account_check.statement_entry import StatementsEntry


def sum_entries(entries: List[StatementsEntry]) -> float:
    result = 0.0
    for entry in entries:
        result += entry.amount
    return result
