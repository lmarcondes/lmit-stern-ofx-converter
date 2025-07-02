from pathlib import Path
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.reader_factory import ReaderFactory
from ofx_converter.parsing.builder import TransactionParserFactory
from tests.base_test_case import BaseTestCase


class ReaderTestCase(BaseTestCase):

    def test_csv_read_transactions(self):

        file = Path("./tests/files/xpi/card/test.csv")
        account_name = "xpi-cartao"
        account = Account(account_name)
        account_config = AccountConfig(account)
        reader = ReaderFactory().make(account_config)
        parser = TransactionParserFactory().make(account)

        transactions = reader.read_transactions(parser, file)
        self.assertIsNotNone(transactions)
        for t in transactions:
            self.assertIsNotNone(t)
            assert t is not None
            self.assertTrue(t.is_valid)
