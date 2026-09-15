from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.builder import TransactionParserFactory
from ofx_converter.parsing.nubank_transaction_parser import NubankTransactionParser
from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser
from ofx_converter.parsing.xp_transaction_parser import (
    XPCardTransactionParser,
    XPTransactionParser,
)
from tests.base_test_case import BaseTestCase


class ParserFactoryTestCase(BaseTestCase):
    def _make(self, account_name: str) -> object:
        config = AccountConfig(account_name)
        return TransactionParserFactory().make(config)

    def test_xpi_conta_uses_xp_parser(self) -> None:
        self.assertIsInstance(self._make("xpi-conta"), XPTransactionParser)

    def test_xpi_investimentos_uses_xp_parser(self) -> None:
        self.assertIsInstance(self._make("xpi-investimentos"), XPTransactionParser)

    def test_xpi_cartao_uses_xp_card_parser(self) -> None:
        self.assertIsInstance(self._make("xpi-cartao"), XPCardTransactionParser)

    def test_nubank_cartao_uses_nubank_parser(self) -> None:
        self.assertIsInstance(self._make("nubank-cartao"), NubankTransactionParser)

    def test_ofx_fallback_returns_ofx_parser(self) -> None:
        self.assertIsInstance(self._make("nubank-conta"), OfxTransactionParser)

    def test_csv_without_specialized_parser_raises(self) -> None:
        config = AccountConfig("xpi-cartao")
        # get_settings() is process-cached, so mutate a local copy rather
        # than the shared settings tree (would corrupt other tests/accounts).
        config._account_settings = dict(config._account_settings)
        config._account_settings["parser"] = "ofx"
        with self.assertRaises(NotImplementedError):
            TransactionParserFactory().make(config)
