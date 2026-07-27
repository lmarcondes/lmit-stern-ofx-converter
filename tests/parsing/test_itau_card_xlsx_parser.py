from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.itau_card_xlsx_parser import ItauCardXlsxParser
from ofx_converter.parsing.transaction import Transaction
from tests.base_test_case import BaseTestCase


_BRT = ZoneInfo("America/Sao_Paulo")


class ItauCardXlsxParserTestCase(BaseTestCase):

    def setUp(self) -> None:
        account_config = AccountConfig("itau-cartao")
        self._parser = ItauCardXlsxParser(account_config)

    def test_parse_purchase(self) -> None:
        record = {
            "Data": datetime(2026, 4, 2, 0, 0),
            "Lançamento": "Rappi*moustache Beamssao Paulobra",
            "Parcelamento": None,
            "Valor": 27.27,
        }

        transaction = self._parser.parse(record)

        self.assertIsInstance(transaction, Transaction)
        assert transaction is not None
        self.assertEqual(transaction.value, Decimal("-27.27"))
        self.assertEqual(
            transaction.timestamp,
            datetime(2026, 4, 2, 0, 0, tzinfo=_BRT),
        )
        self.assertEqual(
            transaction.description, "Rappi*moustache Beamssao Paulobra"
        )

    def test_parse_payment_returns_credit(self) -> None:
        record = {
            "Data": datetime(2026, 3, 12, 0, 0),
            "Lançamento": "Pagamento Com Saldo",
            "Parcelamento": None,
            "Valor": -5000,
        }

        transaction = self._parser.parse(record)

        self.assertIsInstance(transaction, Transaction)
        assert transaction is not None
        self.assertEqual(transaction.value, Decimal("5000.00"))
        self.assertEqual(transaction.transaction_type, "CREDIT")

    def test_parse_installment_appends_parcela_to_description(self) -> None:
        record = {
            "Data": datetime(2026, 4, 1, 0, 0),
            "Lançamento": "Amazon Marketplace",
            "Parcelamento": "Parcela 2 de 3",
            "Valor": 91.19,
        }

        transaction = self._parser.parse(record)

        self.assertIsInstance(transaction, Transaction)
        assert transaction is not None
        self.assertEqual(
            transaction.description,
            "Amazon Marketplace - Parcela 2 de 3",
        )
        self.assertEqual(transaction.value, Decimal("-91.19"))

    def test_skip_empty_row(self) -> None:
        record = {
            "Data": None,
            "Lançamento": None,
            "Parcelamento": None,
            "Valor": None,
        }

        transaction = self._parser.parse(record)

        self.assertIsNone(transaction)
