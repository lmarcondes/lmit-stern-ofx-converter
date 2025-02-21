
from ofx_converter.logger import LogMixin
from ofx_converter.parsing.accounts import Account
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.parsing.xp_transaction_parser import XPCardTransactionParser, XPTransactionParser


class TransactionParserFactory(LogMixin):

    def make(self, account: Account) -> TransactionParser:
        if account == Account.XP_CONTA :
            return XPTransactionParser()
        elif account == Account.XP_CARTAO:
            return XPCardTransactionParser()
