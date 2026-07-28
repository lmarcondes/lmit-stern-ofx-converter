from pathlib import Path

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.builder import TransactionParserFactory
from ofx_converter.parsing.itau_card_xlsx_parser import ItauCardXlsxParser
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.reader_factory import ReaderFactory
from tests.base_test_case import BaseTestCase


class XlsxReaderTestCase(BaseTestCase):

    def test_reads_itau_credit_card_xlsx(self) -> None:
        account_config = AccountConfig("itau-cartao")
        reader = ReaderFactory().make(account_config)
        parser = TransactionParserFactory().make(account_config)

        file = Path("./tests/files/itau/card/fatura-paga-final 4423-abril2026.xlsx")
        transactions = reader.read_transactions(parser, file)

        valid_transactions = [t for t in transactions if t is not None]
        self.assertGreater(len(valid_transactions), 0)
        for transaction in valid_transactions:
            self.assertIsInstance(transaction, Transaction)
            self.assertTrue(transaction.is_valid)

        self.assertIsInstance(parser, ItauCardXlsxParser)
