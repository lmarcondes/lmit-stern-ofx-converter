
from ofx_converter.ofx_client import OfxClient
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from tests.base_test_case import BaseTestCase


class OfxClientTestSuite(BaseTestCase):

    def test_make_template_loader(self) -> None:
        accounts = ['nubank-cartao', 'xpi-conta']
        for account_name in accounts:
            account = Account(account_name)
            account_config = AccountConfig(account)
            client = OfxClient(account_config)
            loader = client._make_template_loader()
            self.assertIsNotNone(loader)
