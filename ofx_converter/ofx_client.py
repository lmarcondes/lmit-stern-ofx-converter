from datetime import datetime
from functools import reduce
from jinja2 import Environment, PackageLoader, Template

from ofx_converter.config import get_settings
from ofx_converter.logger import LogMixin
from ofx_converter.parsing.accounts import Account
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.utils import to_ofx_time


class OfxClient(LogMixin):
    _header_template = "ofx_header.ofx"
    _footer_template = "ofx_footer.ofx"
    _transaction_template = "ofx_transaction.ofx"

    def __init__(self, account: Account, transactions: list[Transaction]) -> None:
        super().__init__()
        self.dtnow = datetime.now().astimezone()
        self._template_reader = Environment(loader=PackageLoader("ofx_converter"))
        self.transactions = sorted(transactions)
        self._settings = get_settings()
        self._account = account
        self._account_settings = self._settings["accounts"][account.value]
        self.log.info("Creating ofx client for account %s", self._account)

    @property
    def header_template(self) -> Template:
        return self._template_reader.get_template(self._header_template)

    @property
    def transaction_template(self) -> Template:
        return self._template_reader.get_template(self._transaction_template)

    @property
    def footer_template(self) -> Template:
        return self._template_reader.get_template(self._footer_template)

    @property
    def ofx_now(self) -> str:
        return to_ofx_time(self.dtnow)

    @property
    def fiorg(self) -> str:
        return self._account_settings["fi"]["org"]

    @property
    def fiid(self) -> str:
        return self._account_settings["fi"]["id"]

    @property
    def bankid(self) -> str:
        return str(self._account_settings["fi"]["id"]).rjust(4, "0")

    @property
    def branchid(self) -> str:
        return self._account_settings["account"]["branch"]

    @property
    def acctid(self) -> str:
        return self._account_settings["account"]["id"]

    @property
    def accttype(self) -> str:
        return str(self._account_settings["account"]["type"]).upper()

    @property
    def lang(self) -> str:
        return str(self._account_settings["lang"]).upper()

    @property
    def cur(self) -> str:
        return str(self._account_settings["cur"]).upper()

    def make_ofx_header(self) -> str:
        self.log.info("Making OFX header for account %s", self._account)
        dtstart = self.transactions[0].ofx_date
        dtend = self.transactions[-1].ofx_date
        payload = {
            "dtnow": self.ofx_now,
            "dtstart": dtstart,
            "dtend": dtend,
            "fiorg": self.fiorg,
            "fiid": self.fiid,
            "bankid": self.bankid,
            "branchid": self.branchid,
            "acctid": self.acctid,
            "accttype": self.accttype,
            "lang": self.lang,
            "cur": self.cur,
        }
        header = self.header_template.render(**payload)
        return header

    def make_ofx_transactions(self) -> list[str]:
        self.log.info("Making OFX transactions for account %s", self._account)
        ofx_transactions = list(
            map(
                lambda x: x.make_ofx_transaction(self.transaction_template),
                self.transactions,
            )
        )
        return ofx_transactions

    def make_ofx_footer(self) -> str:
        self.log.info("Making OFX footer for account %s", self._account)
        dtend = self.transactions[-1].ofx_date
        last_balance = self.transactions[-1].balance
        footer = self.footer_template.render(last_balance=last_balance, dtend=dtend)
        return footer

    def make_ofx_file(self) -> str:
        self.log.info("Making OFX file for account %s", self._account)
        reducer = lambda x, y: x + "\n" + y
        body = reduce(reducer, self.make_ofx_transactions())
        header = self.make_ofx_header()
        footer = self.make_ofx_footer()
        total_file = reduce(reducer, [header, body, footer])
        return total_file
