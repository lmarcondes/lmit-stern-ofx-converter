from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.reader.abstract_reader import AbstractReader
from ofx_converter.reader.csv_reader import CSVReader
from ofx_converter.reader.ofx_reader import OfxReader
from ofx_converter.utils import FileType


class ReaderFactory(LogMixin):

    def make(self, account_config: AccountConfig) -> AbstractReader:
        file_type = account_config.file_format
        reader: AbstractReader
        if file_type == FileType.CSV:
            options = account_config.file_options
            reader = CSVReader(**options)
        elif file_type == FileType.OFX:
            options = account_config.file_options
            reader = OfxReader(**options)
        else:
            raise NotImplementedError()
        return reader
