from ofx_converter.__main__ import run_account_parsing
from ofx_converter.parsing.account import Account
from tests.base_test_case import BaseTestCase


class TestFullConversion(BaseTestCase):

    def test_full_conversion_csv(self) -> None:
        account = Account("nubank-cartao")
        run_account_parsing(account)
