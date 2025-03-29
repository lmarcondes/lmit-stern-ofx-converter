import csv
from pathlib import Path

from ofx_converter.argparser import get_main_parser
from ofx_converter.logger import get_logger
from ofx_converter.ofx_client import OfxClient

from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.builder import TransactionParserFactory
from ofx_converter.parsing.transaction import Transaction

logger = get_logger("main")


def read_transactions(
    parser: TransactionParser, file_path: str
) -> list[Transaction | None]:
    with open(file_path, newline="", mode="r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        transactions = parser.parse_multiple(reader)
    return transactions


def init_settings(account: Account) -> tuple[Path, Path, str]:
    account_config = AccountConfig(account)
    input_path = Path(account_config.file_in)
    if not input_path.exists():
        raise ValueError(f"Input dir is invalid: {input_path}")
    output_path = Path(account_config.file_out)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    file_format = account_config.file_format
    return input_path, output_path, file_format


def csv_to_ofx(account: Account, csv_file_path: Path, ofx_file_path: Path):
    # Read the CSV file
    logger.info("Converting csv to OFX for %s account", account)
    logger.info("Converting from %s to %s", csv_file_path, ofx_file_path)
    parser = TransactionParserFactory().make(account)

    transactions = [
        x for x in read_transactions(parser, csv_file_path.as_posix()) if x is not None
    ]

    if len(transactions) == 0:
        return

    ofx_client = OfxClient(account)

    total_file = ofx_client.make_ofx_file(transactions)

    # Write the OFX file
    logger.info("Writing OFX file with %i transactions", len(transactions))
    with open(ofx_file_path, "w") as ofxfile:
        ofxfile.write(total_file)
        ofxfile.close()


def run(account: Account):
    input_path, output_path, file_format = init_settings(account)
    input_files = [x for x in input_path.iterdir() if x.suffix.endswith(file_format)]
    for file in input_files:
        output_file = output_path / f"{file.stem}.ofx"
        csv_to_ofx(account, file, output_file)


if __name__ == "__main__":
    parser = get_main_parser()
    args, _ = parser.parse_known_args()
    account = Account(args.account)
    run(account)
