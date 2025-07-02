from pathlib import Path

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


def file_to_ofx(account_config: AccountConfig, input_path: Path, output_path: Path):
    # Read the CSV file
    logger.info("Converting file to OFX for %s account", account)
    logger.info("Converting from %s to %s", input_path, output_path)
    parser = TransactionParserFactory().make(account)
    reader = ReaderFactory().make(account_config)

    transactions = [
        x for x in reader.read_transactions(parser, input_path) if x is not None
    ]

    if len(transactions) == 0:
        return

    ofx_client = OfxClient(account)

    total_file = ofx_client.make_ofx_file(transactions)

    # Write the OFX file
    logger.info("Writing OFX file with %i transactions", len(transactions))
    with open(output_path, "w") as ofxfile:
        ofxfile.write(total_file)
        ofxfile.close()


def run(account: Account):
    account_config = init_settings(account)
    file_suffix = account_config.file_format.value
    input_files = [
        x for x in account_config.file_in.iterdir() if x.suffix.endswith(file_suffix)
    ]
    for file in input_files:
        output_file = account_config.file_out / f"{file.stem}.ofx"
        file_to_ofx(account_config, file, output_file)


if __name__ == "__main__":
    parser = get_main_parser()
    args, _ = parser.parse_known_args()
    account = Account(args.account)
    run(account)
