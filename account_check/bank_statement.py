import itertools
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
from PyPDF2 import PdfReader

from account_check.category import Category
from account_check.statement_entry import EntryType, StatementEntry
from account_check.sub_type import SubType

ENTRY_DATE = "date"
ENTRY_AMOUNT = "amount"
ENTRY_TEXT = "text"
ENTRY_TARGET = "target"
ENTRY_TYPE = "type"


class Statement:
    def __init__(
        self,
        entries: List[StatementEntry] = list(),
        file: str = None,
        categories: Dict[str, List[str]] = dict(),
        parse: Dict = None,
        *args,
        **kwargs,
    ) -> None:
        self.entries: List[StatementEntry] = entries
        self.category_definitions = categories
        if file:
            if parse:
                self.parse(file, **parse)
            else:
                self.parse(file, *args, **kwargs)

    def parse(
        self,
        path: str | Path,
        remove_words: List[str],
        remove_lines_with: List[str],
        stop_word: str,
        type_map: Dict[str, str],
    ):
        file = Path(path)
        pdf = PdfReader(file)

        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            lines += _get_cleaned_lines(text, remove_words, remove_lines_with)
        lines = _remove_tailing_information(lines, stop_word)

        lines = [_parse_line(line, type_map) for line in lines]
        lines = _combine_lines(lines)
        _cleanup_text(lines)
        self.entries = [_to_statements_entry(line) for line in lines]
        self.set_categories()

    def set_categories(self):
        for entry in self.entries:
            entry.category = self.get_category(entry)

    def get_categories(self) -> List[Category]:
        result = self._get_categories()

        # Calculate sums
        totals = {}
        for kind, categories in result.items():
            sum = 0
            for category in categories:
                sum += category.amount
            totals[kind] = sum

        # Set totals in categories
        for kind, categories in result.items():
            for category in categories:
                category.relative_total = totals[kind]

        return list(itertools.chain.from_iterable(result.values()))

    def _get_categories(self) -> Dict[str, List[Category]]:
        categories: Dict[str, Dict[str, Category]] = {}
        for entry in self.entries:
            kind = (
                EntryType.CREDIT if entry.kind == EntryType.CREDIT else EntryType.DEBIT
            )
            if kind not in categories:
                categories[kind] = {}
            kind = categories[kind]
            category = entry.category
            if category not in kind:
                kind[category] = Category(category)
            kind[category].append(entry)
        result = {
            name: list(category_entries.values())
            for name, category_entries in categories.items()
        }
        return result

    def get_categories_dataframe(self) -> pd.DataFrame:
        categories = [
            {
                "category": category.name,
                "amount": category.amount,
                "month": self.last.month,
                "percent": f"{category.relative:.2%}",
            }
            for category in self.get_categories()
        ]
        return pd.DataFrame(categories)

    @property
    def debits(self) -> List[StatementEntry]:
        return [
            entry
            for entry in self.entries
            if entry.kind == EntryType.TRANSFER or entry.kind == EntryType.DEBIT
        ]

    @property
    def debit(self):
        return SubType(self.debits)

    @property
    def credits(self) -> List[StatementEntry]:
        return [entry for entry in self.entries if entry.kind == EntryType.CREDIT]

    @property
    def credit(self):
        return SubType(self.credits)

    @property
    def profit(self) -> float:
        return self.credit + self.debit

    @property
    def first(self) -> StatementEntry:
        return min(self.entries, key=lambda x: x.date)

    @property
    def last(self) -> StatementEntry:
        return max(self.entries, key=lambda x: x.date)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.first.date} - {self.last.date}\tin:{self.credit:.2f}\tout:{self.debit:.2f}\tbalance:{self.profit:.2f}"

    def get_category(self, entry: StatementEntry) -> str:
        for category, category_entries in self.category_definitions.items():
            if any(
                [
                    cat_entry in entry.target or cat_entry in entry.text
                    for cat_entry in category_entries
                ]
            ):
                return category
        return "Sonstige"

    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([entry.dict() for entry in self.entries])


def _get_cleaned_lines(
    text: str, remove_words: List[str], remove_lines_with: List[str]
) -> List[str]:
    for entry in remove_words:
        text = text.replace(entry, "")

    lines = [
        line
        for line in text.splitlines()
        if line and all([entry not in line for entry in remove_lines_with])
    ]

    return lines


def _remove_tailing_information(
    lines: List[Dict],
    stop_word: str,
) -> List[Dict]:
    return lines[: lines.index(stop_word)]


def _parse_line(line: str, type_map: Dict[str, str]):
    parts = line.split()

    date_ = None
    try:
        date_ = datetime.strptime(parts[0], "%d.%m.%Y").date()
    except ValueError:
        pass
    else:
        parts = parts[1:] if len(parts) > 1 else []

    type_ = None
    if parts and parts[0] in type_map:
        type_ = EntryType(type_map[parts[0]])
        parts = parts[1:] if len(parts) > 1 else []

    amount = None
    if parts and type_:
        try:
            amount = parts[-1].replace(".", "").replace(",", ".")
            amount = float(amount)
        except ValueError:
            pass
        else:
            parts = parts[:-1]

    result = {}
    if type_:
        result[ENTRY_TEXT] = []
        result[ENTRY_DATE] = date_
        result[ENTRY_TYPE] = type_
        result[ENTRY_AMOUNT] = amount

        result[ENTRY_TARGET] = " ".join(parts)

    else:
        result[ENTRY_TEXT] = parts

    return result


def _combine_lines(lines: List[Dict]) -> List[Dict]:
    result = []
    for line in lines:
        if ENTRY_TYPE in line:
            result.append(line)
        elif ENTRY_TEXT in line:
            result[-1][ENTRY_TEXT] += line[ENTRY_TEXT]
    return result


def _cleanup_text(lines: List[Dict]):
    for line in lines:
        line[ENTRY_TEXT] = " ".join(line[ENTRY_TEXT])


def _to_statements_entry(line: Dict):
    return StatementEntry(
        amount=line[ENTRY_AMOUNT],
        date=line[ENTRY_DATE],
        target=line[ENTRY_TARGET],
        text=line[ENTRY_TEXT],
        kind=line[ENTRY_TYPE],
        category=None,
    )
