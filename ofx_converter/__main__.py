from collections.abc import Callable
import csv
from datetime import datetime
from dataclasses import dataclass
from functools import reduce
from typing import Any
from hashlib import md5
from base64 import b64encode
from jinja2 import Environment, PackageLoader, Template
from re import compile


class Templater:
    def __init__(self) -> None:
        self.env = Environment(loader=PackageLoader("ofx_converter"))


@dataclass
class Transaction:
    timestamp: datetime
    description: str
    value: float
    balance: float
    transaction_id: str | None = None

    _timestamp_format = "%Y%m%d%H%M%S"

    @property
    def transaction_type(self) -> str:
        return "DEBIT" if self.value < 0 else "CREDIT"

    @property
    def ofx_date(self) -> str:
        return self.timestamp.strftime(self._timestamp_format)

    @property
    def fitid(self) -> str:
        if self.transaction_id is not None:
            return self.transaction_id
        key = "-".join(
            map(
                lambda x: str(x),
                [self.timestamp.isoformat(), self.description, self.value],
            )
        )
        digest = b64encode(md5(key.encode()).digest()).decode()
        return digest

    def make_ofx_transaction(self, template: Template):
        payload = {
            "trn_type": self.transaction_type,
            "dt_posted": self.ofx_date,
            "amount": self.value,
            "desc": self.description,
            "fitid": self.fitid,
        }
        trn_formatted = template.render(**payload)
        return trn_formatted

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Transaction):
            return self.timestamp < other.timestamp
        else:
            raise ValueError(f"Can't compare Transaction to type {type(other)}")


class TransactionParser:
    DATE_COL = "Data"
    DESCRIPTION_COL = "Descricao"
    VALUE_COL = "Valor"
    BALANCE_COL = "Saldo"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{2})[\\s\\w]+(?P<hour>\\d{2}):(?P<min>\\d{2}):(?P<sec>\\d{2})$"
    _value_pattern = "(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$"

    def __init__(self) -> None:
        self._date_regex = compile(self._date_pattern)
        self._value_regex = compile(self._value_pattern)

    def _parse_date(self, date: str) -> datetime | None:
        date_obj = self._date_regex.match(date)
        if date_obj is None:
            return None
        date_string = "20{year}-{month}-{day}T{hour}:{min}:{sec}.000-03:00".format(
            **date_obj.groupdict()
        )
        date_converted = datetime.fromisoformat(date_string)
        return date_converted

    def _parse_money(self, value: str) -> float | None:
        value_obj = self._value_regex.match(value)
        if value_obj is None:
            return None
        value_extracted = value_obj["value"].replace(".", "").replace(",", ".")
        sign_extracted = value_obj.groupdict().get("sign")
        value_converted = float(
            "{sign}{value}".format(
                sign=sign_extracted if sign_extracted is not None else "",
                value=value_extracted,
            )
        )
        return value_converted

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        (date, desc, value, balance) = (
            record[self.DATE_COL],
            record[self.DESCRIPTION_COL],
            record[self.VALUE_COL],
            record[self.BALANCE_COL],
        )
        date_parsed = self._parse_date(date)
        value_converted = self._parse_money(value)
        balance_converted = self._parse_money(balance)
        valid_conversions = map(
            lambda x: x is not None, [date_parsed, value_converted, balance_converted]
        )
        reducer: Callable[[bool, bool], bool] = lambda x, y: x and y
        is_valid_transaction = reduce(reducer, valid_conversions)
        if not is_valid_transaction:
            return None
        transaction = Transaction(date_parsed, desc, value_converted, balance_converted)  # type: ignore
        return transaction


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
