
from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.xp_transaction_parser import XPCardTransactionParser, XPTransactionParser


class TransactionParserFactory(LogMixin):

    def make(self, account: Account) -> TransactionParser:
        account_config = AccountConfig(account)
        if account == Account.XP_CONTA :
            parser = XPTransactionParser(account_config)
        elif account == Account.XP_CARTAO:
            parser = XPCardTransactionParser(account_config)
        elif account == Account.XP_INVESTIMENTOS:
            parser = XPTransactionParser(account_config)
        return parser
