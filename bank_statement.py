from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List

from PyPDF2 import PdfReader

ENTRY_DATE = "date"
ENTRY_AMOUNT = "amount"
ENTRY_TEXT = "text"
ENTRY_TARGET = "target"
ENTRY_TYPE = "type"


class EntryType(Enum):
    CREDIT = "Gutschrift"
    TRANSFER = "Ueberweisung"
    DEBIT = "Lastschrift"


@dataclass
class StatementsEntry:
    amount: float
    date: date
    target: str
    text: str
    kind: EntryType


class Statement:
    def __init__(self, entries: List[StatementsEntry] = list()) -> None:
        self.entries: List[StatementsEntry] = entries

    def parse(
        self,
        path: str | Path,
        remove_words: List[str],
        remove_lines_with: List[str],
        stop_word: str,
    ):
        file = Path(path)
        pdf = PdfReader(file)

        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            lines += _get_cleaned_lines(text, remove_words, remove_lines_with)
        lines = _remove_tailing_information(lines, stop_word)

        lines = [_parse_line(line) for line in lines]
        lines = _combine_lines(lines)
        _cleanup_text(lines)
        self.entries = [_to_statements_entry(line) for line in lines]

    @property
    def debits(self) -> List[StatementsEntry]:
        return [
            entry
            for entry in self.entries
            if entry.kind == EntryType.TRANSFER or entry.kind == EntryType.DEBIT
        ]

    @property
    def debit(self) -> float:
        return sum_entries(self.debits)

    @property
    def credits(self) -> List[StatementsEntry]:
        return [entry for entry in self.entries if entry.kind == EntryType.CREDIT]

    @property
    def credit(self) -> float:
        return sum_entries(self.credits)

    @property
    def profit(self) -> float:
        return self.credit + self.debit


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


def _parse_line(line: str):
    parts = line.split()

    date_ = None
    try:
        date_ = datetime.strptime(parts[0], "%d.%m.%Y").date()
    except ValueError:
        pass
    else:
        parts = parts[1:] if len(parts) > 1 else []

    type_ = None
    if parts and parts[0] in [type_.value for type_ in EntryType]:
        type_ = EntryType(parts[0])
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
    return StatementsEntry(
        amount=line[ENTRY_AMOUNT],
        date=line[ENTRY_DATE],
        target=line[ENTRY_TARGET],
        text=line[ENTRY_TEXT],
        kind=line[ENTRY_TYPE],
    )


def sum_entries(entries: List[StatementsEntry]) -> float:
    result = 0.0
    for entry in entries:
        result += entry.amount
    return result
