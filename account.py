from pathlib import Path
from typing import List

from bank_statement import Statement


class Account:
    def __init__(self, config) -> None:
        self.statements: List[Statement] = []
        self.config = config

    def read_statements(self, dir: str):
        for file in Path(dir).glob("*.pdf"):
            self.statements.append(Statement(file=file, **self.config["parse"]))