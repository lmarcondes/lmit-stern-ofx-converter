from typing import Any, Type

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.nubank_transaction_parser import NubankTransactionParser
from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser
from ofx_converter.parsing.parser_type import ParserType
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.xp_transaction_parser import (
    XPCardTransactionParser,
    XPTransactionParser,
)
from ofx_converter.utils import FileType


class TransactionParserFactory(LogMixin):

    _parser_map: dict[ParserType, Type[TransactionParser[Any]]] = {
        ParserType.XP_CSV: XPTransactionParser,
        ParserType.XP_CARD_CSV: XPCardTransactionParser,
        ParserType.NUBANK_OFX: NubankTransactionParser,
    }

    def make(self, account_config: AccountConfig) -> TransactionParser[Any]:
        parser_type = account_config.parser
        if parser_type in self._parser_map:
            return self._parser_map[parser_type](account_config)
        elif account_config.file_format == FileType.OFX:
            return OfxTransactionParser(account_config)
        else:
            raise NotImplementedError(
                "Parser for account %s (parser=%s) not implemented",
                account_config.account,
                parser_type,
            )
