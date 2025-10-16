import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator

from click import argument, command, group, option
from dateutil.relativedelta import relativedelta

from ofx_converter.argparser import get_main_parser
from ofx_converter.logger import get_logger
from ofx_converter.ofx_client import OfxClient
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.builder import TransactionParserFactory
from ofx_converter.reader_factory import ReaderFactory

logger = get_logger("main")


def init_settings(account: Account) -> AccountConfig:
    account_config = AccountConfig(account)
    input_path = Path(account_config.file_in)
    if not input_path.exists():
        raise ValueError(f"Input dir is invalid: {input_path}")
    output_path = Path(account_config.file_out)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    return account_config


def file_to_ofx(
    account_config: AccountConfig, input_path: Path, output_path: Path
) -> Path | None:
    # Read the CSV file
    logger.info("Converting file to OFX for %s account", account_config.account)
    logger.info("Converting from %s to %s", input_path, output_path)
    parser = TransactionParserFactory().make(account_config)
    reader = ReaderFactory().make(account_config)

    transactions = [
        x for x in reader.read_transactions(parser, input_path) if x is not None
    ]

    if len(transactions) == 0:
        return None

    ofx_client = OfxClient(account_config)

    total_file = ofx_client.make_ofx_file(transactions)

    # Write the OFX file
    logger.info("Writing OFX file with %i transactions", len(transactions))
    with open(output_path, "w") as ofxfile:
        ofxfile.write(total_file)
        ofxfile.close()
    return output_path


def filter_files_with_dates(
    files: list[Path], from_date: datetime | None, to_date: datetime | None
) -> list[Path]:
    if from_date is None and to_date is None:
        return files

    def is_within_range(file: Path) -> bool:
        date_match = re.search("(?P<year>\\d{4})-(?P<month>\\d{2})", file.name)
        if date_match is None:
            return False
        year, month = date_match.group("year"), date_match.group("month")
        date = datetime(year=int(year), month=int(month), day=1)
        if from_date is None:
            assert to_date is not None
            return date <= to_date
        elif to_date is None:
            return from_date <= date
        else:
            return from_date <= date and date <= to_date

    filtered_files = list(filter(is_within_range, files))
    return filtered_files


def run_account_parsing(
    account: Account, from_date: datetime | None = None, to_date: datetime | None = None
) -> Generator[Path | None, None, None]:
    account_config = init_settings(account)
    file_suffix = account_config.file_format.value
    input_files = [
        x for x in account_config.file_in.iterdir() if x.suffix.endswith(file_suffix)
    ]
    filtered_files = filter_files_with_dates(input_files, from_date, to_date)
    for file in filtered_files:
        output_file = account_config.file_out / f"{file.stem}.ofx"
        yield file_to_ofx(account_config, file, output_file)


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
    account: Account = Account(account_name)
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
    run_account_parsing(account, parsed_from_date, parsed_to_date)
