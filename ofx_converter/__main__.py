import csv
from datetime import datetime
from functools import reduce
from typing import Any
from jinja2 import Environment, PackageLoader
from .transaction_parser import TransactionParser
from .transaction import Transaction


class Templater:
    def __init__(self) -> None:
        self.env = Environment(loader=PackageLoader("ofx_converter"))


def read_transactions(file_path) -> list[Transaction | None]:
    parser = TransactionParser()

    def mapper(row: dict[str, Any]) -> Transaction | None:
        parsed = parser.parse(row)
        return parsed

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        transactions = list(map(mapper, reader))
    return transactions


def csv_to_ofx(csv_file_path, ofx_file_path):
    template_reader = Templater()
    # Read the OFX header and footer templates
    ofx_header_template = template_reader.env.get_template("ofx_header.txt")
    ofx_footer_template = template_reader.env.get_template("ofx_footer.txt")
    ofx_transaction_template = template_reader.env.get_template("ofx_transaction.txt")

    # Read the CSV file
    transactions = sorted(
        [x for x in read_transactions(csv_file_path) if x is not None]
    )

    if len(transactions) == 0:
        return

    ofx_transactions = list(
        map(lambda x: x.make_ofx_transaction(ofx_transaction_template), transactions)
    )

    # Get the start and end dates for the transactions
    dtstart = transactions[0].ofx_date
    dtend = transactions[-1].ofx_date
    dtnow = datetime.now().strftime("%Y%m%d%H%M%S")

    header = ofx_header_template.render(dtnow=dtnow, dtstart=dtstart, dtend=dtend)
    body = reduce(lambda x, y: x + "\n" + y, ofx_transactions)
    footer = ofx_footer_template.render(balance=transactions[-1].balance, dtend=dtend)
    # Write the OFX file
    with open(ofx_file_path, "w") as ofxfile:
        ofxfile.write(header)
        ofxfile.write(body)
        ofxfile.write(footer)
        ofxfile.close()


if __name__ == "__main__":
    csv_to_ofx("transactions.csv", "transactions.ofx")
