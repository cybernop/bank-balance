from datetime import date
from pathlib import Path

import plotly.express as px
import yaml

from account_check.account import Account

if __name__ == "__main__":
    config = yaml.safe_load(Path("config.yml").read_text())

    account = Account(config=config)
    account.read_statements(config["statement_dir"])

    data = account.dataframe()
    first_date = date(day=1, month=7, year=2022)
    data = data[data["month"] >= first_date]

    fig = px.bar(
        data,
        x="month",
        y="amount",
        color="category",
        hover_name="description",
    )
    fig.show()
    input("any key to close...")
