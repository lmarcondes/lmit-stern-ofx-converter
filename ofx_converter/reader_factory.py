from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.reader import AbstractReader, CSVReader
from ofx_converter.utils import FileType


class ReaderFactory(LogMixin):

    def make(self, account_config: AccountConfig) -> AbstractReader:
        file_type = account_config.file_format
        if file_type == FileType.CSV:
            options = account_config.file_options
            reader = CSVReader(**options)
        else:
            raise NotImplementedError()
        return reader
