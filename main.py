from datetime import datetime
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


def parse(
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
        lines += get_cleaned_lines(text, remove_words, remove_lines_with)
    lines = remove_tailing_information(lines, stop_word)

    lines = [parse_line(line) for line in lines]
    lines = combine_lines(lines)
    return cleanup_text(lines)


def get_cleaned_lines(
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


def remove_tailing_information(
    lines: List[Dict],
    stop_word: str,
) -> List[Dict]:
    return lines[: lines.index(stop_word)]


def parse_line(line: str):
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


def combine_lines(lines: List[Dict]) -> List[Dict]:
    result = []
    for line in lines:
        if ENTRY_TYPE in line:
            result.append(line)
        elif ENTRY_TEXT in line:
            result[-1][ENTRY_TEXT] += line[ENTRY_TEXT]
    return result


def cleanup_text(lines: List[Dict]):
    for line in lines:
        line[ENTRY_TEXT] = " ".join(line[ENTRY_TEXT])