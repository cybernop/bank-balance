from pathlib import Path

import plotly.express as px
import yaml

from account_check.account import Account

if __name__ == "__main__":
    config = yaml.safe_load(Path("config.yml").read_text())

    account = Account(config=config)
    account.read_statements(config["statement_dir"])

    data = account.debit.dataframe()

    fig = px.bar(
        data,
        x="month",
        y="amount",
        color="category",
        hover_name="target",
    )
    fig.show()
    input("any key to close...")
