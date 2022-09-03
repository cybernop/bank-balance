from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from typing import Dict

import pandas as pd


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
        return {"month": self.month, "description": self.description, **asdict(self)}

    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self.dict()])

    @property
    def description(self) -> str:
        return f"{self.target}: {self.text}"
