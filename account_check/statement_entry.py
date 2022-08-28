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
