from pathlib import Path
from typing import Any

from ofxparse import Account, OfxParser, Statement
from ofxparse import Transaction as OfxTransaction
from ofxparse.ofxparse import Ofx

from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.reader.abstract_reader import BaseReader


class OfxReader(BaseReader):

    def __init__(self, encoding: str, **_: Any) -> None:
        super().__init__()
        self._encoding = encoding

    def _read_ofx(self, file_path: Path) -> Ofx:
        with open(file_path, mode="r", encoding=self._encoding) as file_obj:
            ofx_file = OfxParser.parse(file_obj)
            file_obj.close()
        return ofx_file

    def read_transactions(
        self, parser: TransactionParser[OfxTransaction], file_path: Path
    ) -> list[Transaction | None]:
        ofx = self._read_ofx(file_path)
        account: Account = ofx.account
        statement: Statement = account.statement
        transactions: list[OfxTransaction] = statement.transactions
        parsed = parser.parse_multiple(transactions)
        return parsed
