from typing import Dict

import pandas as pd

from account_check.category import Category
from account_check.helpers import sum_entries


class SubType:
    def __init__(self, value) -> None:
        self.value = value

    @property
    def categories(self) -> Dict[str, Category]:
        return get_categories(self.value)

    @property
    def total(self) -> float:
        return sum_entries(self.value)

    def dataframe(self):
        return pd.DataFrame([entry.dict() for entry in self.value])


def get_categories(entries) -> Dict[str, Category]:
    categories = {}

    for entry in entries:
        category = entry.category
        if category not in categories:
            categories[category] = Category()
        categories[category].append(entry)

    return categories
