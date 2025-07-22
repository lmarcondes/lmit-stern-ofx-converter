
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser
from tests.base_test_case import BaseTestCase


class OfxTransactionParserTestSuite(BaseTestCase):

    def test_installment_id(self) -> None:
        tran_id = "6766cf6e-3ac9-40da-8f1a-164426f32192"
        memo = "Lj do Mec - Parcela 9/10"
        account_name = "nubank-cartao"
        account = Account(account_name)
        account_config = AccountConfig(account)
        parser = OfxTransactionParser(account_config)
        new_tran_id = parser.installment_id(tran_id, memo)
        self.assertIsNone(new_tran_id)
        self.assertNotEqual(new_tran_id, tran_id)
