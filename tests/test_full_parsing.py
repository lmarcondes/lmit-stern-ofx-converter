from datetime import datetime
from typing import Callable

from ofxparse import OfxParser

from ofx_converter import filter_files_with_dates, run_account_parsing
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from tests.base_test_case import BaseTestCase


class TestFullConversion(BaseTestCase):

    def setUp(self) -> None:
        self._ofx_parser = OfxParser()

    def test_full_conversion_csv(self) -> None:
        account = Account("nubank-cartao")
        run_account_parsing(account)
        paths = list(run_account_parsing(account))
        for x in paths:
            self.assertIsNotNone(x)

    def test_full_conversion_csv_with_dates(self) -> None:
        account = Account("nubank-cartao")
        parse_date: Callable[[str], datetime] = lambda dt: datetime.strptime(dt, "%Y-%m")
        from_date, to_date = parse_date("2025-03"), parse_date("2025-04")
        paths = list(run_account_parsing(account, from_date, to_date))
        for path in paths:
            self.assertIsNotNone(path)
            if path is not None:
                with open(path, 'rb') as of:
                    ofx = self._ofx_parser.parse(of)
                    of.close()
                self.assertIsNotNone(ofx)


    def test_date_filter(self) -> None:
        account = Account("nubank-cartao")
        account_config = AccountConfig(account)
        parse_date: Callable[[str], datetime] = lambda dt: datetime.strptime(dt, "%Y-%m")
        from_date, to_date = parse_date("2025-03"), parse_date("2025-04")
        file_suffix = account_config.file_format.value
        input_files = [
            x for x in account_config.file_in.iterdir() if x.suffix.endswith(file_suffix)
        ]
        self.assertEqual(len(input_files), 2)
        filtered_files = filter_files_with_dates(input_files, from_date, to_date)
        self.assertEqual(len(filtered_files), 1)


