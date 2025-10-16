import re
from datetime import datetime
from typing import Callable

from click import argument, group, option
from dateutil.relativedelta import relativedelta

from ofx_converter.logger import get_logger
from ofx_converter.parsing.account import Account
from ofx_converter.runner import Runner

logger = get_logger("main")

@group("main")
def main() -> None:
    pass


@main.command("convert")
@argument("account_name", type=str, required=True)
@option("--from_date", type=str, required=False)
@option("--to_date", type=str, required=False)
def convert(
    account_name: str, from_date: str | None = None, to_date: str | None = None
) -> None:
    """Converts files for a given account name

    Args:
        account_name: name of the account
        from_date: month to convert files from
        to_date: month to convert files until
    """
    current_date = datetime.today()

    parse_date: Callable[[str], datetime] = lambda dt: (datetime.strptime(dt, "%Y-%m"))
    parsed_from_date: datetime = (
        parse_date(from_date) if from_date else (current_date - relativedelta(months=5))
    )
    parsed_to_date: datetime = parse_date(to_date) if to_date else current_date
    logger.info(
        "Converting account %s from date %s to date %s",
        account_name,
        parsed_from_date.isoformat(),
        parsed_to_date.isoformat(),
    )
    runner = Runner(account_name)
    runner.run_account_parsing(parsed_from_date, parsed_to_date)
