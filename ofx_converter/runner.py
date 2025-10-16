import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator

from dateutil.relativedelta import relativedelta

from ofx_converter.logger import LogMixin
from ofx_converter.ofx_client import OfxClient
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.builder import TransactionParserFactory
from ofx_converter.reader_factory import ReaderFactory


class Runner(LogMixin):

    def __init__(self, account_name: str) -> None:
        super().__init__()
        account: Account = Account(account_name)
        self.log.info(
            "Instantiating runner with account %s",
            account_name,
        )
        self.account = account
        self.account_config = self.init_settings()

    def init_settings(self) -> AccountConfig:
        account_config = AccountConfig(self.account)
        input_path = Path(account_config.file_in)
        if not input_path.exists():
            raise ValueError(f"Input dir is invalid: {input_path}")
        output_path = Path(account_config.file_out)
        if not output_path.exists():
            output_path.mkdir(parents=True)
        return account_config

    def file_to_ofx(self, input_path: Path, output_path: Path) -> Path | None:
        # Read the CSV file
        account_config = self.account_config
        self.log.info("Converting file to OFX for %s account", account_config.account)
        self.log.info("Converting from %s to %s", input_path, output_path)
        parser = TransactionParserFactory().make(account_config)
        reader = ReaderFactory().make(account_config)

        transactions = [
            x for x in reader.read_transactions(parser, input_path) if x is not None
        ]

        if len(transactions) == 0:
            return None

        ofx_client = OfxClient(account_config)

        total_file = ofx_client.make_ofx_file(transactions)

        # Write the OFX file
        self.log.info("Writing OFX file with %i transactions", len(transactions))
        with open(output_path, "w") as ofxfile:
            ofxfile.write(total_file)
            ofxfile.close()
        return output_path

    def filter_files_with_dates(
        self, files: list[Path], from_date: datetime | None, to_date: datetime | None
    ) -> list[Path]:
        if from_date is None and to_date is None:
            return files

        def is_within_range(file: Path) -> bool:
            date_match = re.search("(?P<year>\\d{4})-(?P<month>\\d{2})", file.name)
            if date_match is None:
                return False
            year, month = date_match.group("year"), date_match.group("month")
            date = datetime(year=int(year), month=int(month), day=1)
            if from_date is None:
                assert to_date is not None
                return date <= to_date
            elif to_date is None:
                return from_date <= date
            else:
                return from_date <= date and date <= to_date

        filtered_files = list(filter(is_within_range, files))
        return filtered_files

    def run_account_parsing(
        self, from_date: datetime | None = None, to_date: datetime | None = None
    ) -> Generator[Path | None, None, None]:
        account_config = self.init_settings()
        file_suffix = account_config.file_format.value
        input_files = [
            x
            for x in account_config.file_in.iterdir()
            if x.suffix.endswith(file_suffix)
        ]
        filtered_files = self.filter_files_with_dates(input_files, from_date, to_date)
        for file in filtered_files:
            output_file = account_config.file_out / f"{file.stem}.ofx"
            yield self.file_to_ofx(file, output_file)
