from pathlib import Path
from typing import List

import pandas as pd

from account_check.bank_statement import Statement
from account_check.sub_type import SubType


class Account:
    def __init__(self, config) -> None:
        self.statements: List[Statement] = []
        self.config = config

    def read_statements(self, dir: str):
        for file in Path(dir).glob("*.pdf"):
            self.statements.append(
                Statement(
                    file=file,
                    categories=self.config["categories"],
                    parse=self.config["parse"],
                )
            )

    def dataframe(self) -> pd.DataFrame:
        return pd.concat([statement.dataframe() for statement in self.statements])

    def categories_dataframe(self) -> pd.DataFrame:
        return pd.concat(
            [statement.get_categories_dataframe() for statement in self.statements]
        )

    @property
    def credit(self):
        list_ = []
        for entry in self.statements:
            list_ += entry.credit.value
        return SubType(list_)

    @property
    def debit(self):
        list_ = []
        for entry in self.statements:
            list_ += entry.debit.value
        return SubType(list_)
