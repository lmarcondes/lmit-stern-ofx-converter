from typing import Any, Type

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.nubank_transaction_parser import NubankTransactionParser
from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.xp_transaction_parser import (
    XPCardTransactionParser,
    XPTransactionParser,
)
from ofx_converter.utils import FileType


class TransactionParserFactory(LogMixin):

    _parser_map: dict[Account, Type[TransactionParser[Any]]] = {
        Account.XP_CONTA: XPTransactionParser,
        Account.XP_CARTAO: XPCardTransactionParser,
        Account.XP_INVESTIMENTOS: XPTransactionParser,
        Account.NUBANK_CARD: NubankTransactionParser,
    }

    def make(self, account_config: AccountConfig) -> TransactionParser[Any]:
        account = account_config.account
        if account in self._parser_map:
            return self._parser_map[account](account_config)
        elif account_config.file_format == FileType.OFX:
            return OfxTransactionParser(account_config)
        else:
            raise NotImplementedError("Parser for account %s not implemented", account)
