from datetime import date
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as po
import yaml
from dash import Dash, Input, Output, dcc, html

from account_check.account import Account


def get_config():
    return yaml.safe_load(Path("config.yml").read_text())


def create_account(config) -> Account:
    account = Account(config=config)
    account.read_statements(config["statement_dir"])
    return account


def get_categories(account: Account, not_before: date = None) -> po.Figure:
    data = account.categories_dataframe()

    if not_before is not None:
        data = filter_data(data, not_before)

    figure = px.bar(
        data,
        x="month",
        y="amount",
        color="category",
        hover_name="category",
        hover_data=["percent"],
    )

    return figure


def get_details(account: Account, not_before: date = None) -> po.Figure:
    data = account.dataframe()

    if not_before is not None:
        data = filter_data(data, not_before)

    figure = px.bar(
        data,
        x="month",
        y="amount",
        color="category",
        hover_name="description",
        hover_data=["date"],
    )

    return figure


def filter_data(df: pd.DataFrame, not_before: date) -> pd.DataFrame:
    return df[df["month"] >= not_before]


def build_app(figures: Dict[str, po.Figure]) -> Dash:
    app = Dash("Account Check")

    app.layout = html.Div(
        [
            html.H4("Account Check"),
            html.P("Select display type:"),
            dcc.Dropdown(
                id="dropdown",
                options=["Categories", "Details"],
                value="Categories",
                clearable=False,
            ),
            dcc.Graph(id="graph"),
        ]
    )

    @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
    def display_graph(type_):
        fig = figures[type_]
        fig.update_layout(height=1000)
        return fig

    return app


def main():
    config = get_config()
    account = create_account(config)

    not_before = date(day=1, month=7, year=2022)
    figures = {
        "Categories": get_categories(account, not_before),
        "Details": get_details(account, not_before),
    }

    app = build_app(figures)

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
