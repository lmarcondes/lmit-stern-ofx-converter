from typing import Any

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.xp_transaction_parser import (
    XPCardTransactionParser,
    XPTransactionParser,
)
from ofx_converter.utils import FileType


class TransactionParserFactory(LogMixin):

    def make(self, account_config: AccountConfig) -> TransactionParser[Any]:
        account = account_config.account
        if account == Account.XP_CONTA:
            return XPTransactionParser(account_config)
        elif account == Account.XP_CARTAO:
            return XPCardTransactionParser(account_config)
        elif account == Account.XP_INVESTIMENTOS:
            return XPTransactionParser(account_config)
        elif account == Account.NUBANK_CARD:
            return OfxTransactionParser(account_config)
        elif account_config.file_format == FileType.OFX:
            return OfxTransactionParser(account_config)
        else:
            raise NotImplementedError("Parser for account %s not implemented", account)
