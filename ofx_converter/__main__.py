import csv
from typing import Any

from ofx_converter.ofx_client import OfxClient
from .transaction_parser import TransactionParser
from .transaction import Transaction


def read_transactions(file_path: str) -> list[Transaction | None]:
    parser = TransactionParser()

    def mapper(row: dict[str, Any]) -> Transaction | None:
        parsed = parser.parse(row)
        return parsed

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        transactions = list(map(mapper, reader))
    return transactions


def csv_to_ofx(account, csv_file_path, ofx_file_path):
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


if __name__ == "__main__":
    csv_to_ofx("xpi-conta", "transactions.csv", "transactions.ofx")
