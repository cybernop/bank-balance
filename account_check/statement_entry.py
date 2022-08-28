from dataclasses import dataclass
from datetime import date
from enum import Enum


class EntryType(Enum):
    CREDIT = "Credit"
    TRANSFER = "Transfer"
    DEBIT = "Debit"


@dataclass
class StatementEntry:
    amount: float
    date: date
    target: str
    text: str
    kind: EntryType
    category: str

    def __hash__(self) -> int:
        return hash(self.amount) + hash(self.date) + hash(self.kind)

    @property
    def month(self) -> date:
        return date(day=1, month=self.date.month, year=self.date.year)
