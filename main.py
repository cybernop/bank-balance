from pathlib import Path

import yaml

from account import Account

if __name__ == "__main__":
    config = yaml.safe_load(Path("config.yml").read_text())

    account = Account(config=config)
    account.read_statements(config["statement_dir"])
    pass
