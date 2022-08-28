from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from typing import Dict


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
        return hash(frozenset(self.dict().items()))

    @property
    def month(self) -> date:
        return date(day=1, month=self.date.month, year=self.date.year)

    def dict(self) -> Dict[str, str]:
        return {"month": self.month, **asdict(self)}
