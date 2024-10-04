import csv
from typing import Any
from pathlib import Path

from ofx_converter.ofx_client import OfxClient
from .transaction_parser import TransactionParser
from .transaction import Transaction
from .config import get_settings


def read_transactions(file_path: str) -> list[Transaction | None]:
    parser = TransactionParser()

    def mapper(row: dict[str, Any]) -> Transaction | None:
        parsed = parser.parse(row)
        return parsed

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        transactions = list(map(mapper, reader))
    return transactions

def init_settings(account: str) -> tuple[Path, Path, str]:
    settings = get_settings()
    file_settings = settings['accounts'][account]['files']
    input_path = Path(file_settings['in'])
    if not input_path.exists():
        raise ValueError(f"Input dir is invalid: {input_path}")
    output_path = Path(file_settings['out'])
    if not output_path.exists():
        output_path.mkdir(parents=True)
    file_format = file_settings['format']
    return input_path, output_path, file_format

def csv_to_ofx(account: str, csv_file_path:str, ofx_file_path:str):
    # Read the CSV file
    transactions = sorted(
        [x for x in read_transactions(csv_file_path) if x is not None]
    )

    if len(transactions) == 0:
        return

    ofx_client = OfxClient(account, transactions)

    total_file = ofx_client.make_ofx_file()

    # Write the OFX file
    with open(ofx_file_path, "w") as ofxfile:
        ofxfile.write(total_file)
        ofxfile.close()

def run(account: str):
    input_path, output_path, file_format = init_settings(account)
    input_files = [x for x in input_path.iterdir() if x.suffix.endswith(file_format)]
    for file in input_files:
        output_file = output_path / f"{file.stem}.ofx"
        csv_to_ofx(account, file.absolute().as_posix(), output_file.absolute().as_posix())

if __name__ == "__main__":
    run("xpi-conta")
