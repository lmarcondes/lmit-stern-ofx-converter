from datetime import datetime
from functools import reduce
from typing import Callable

from jinja2 import BaseLoader, ChoiceLoader, Environment, PackageLoader, Template

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.utils import to_ofx_time


class OfxClient(LogMixin):
    _header_template = "ofx_header.ofx"
    _footer_template = "ofx_footer.ofx"
    _transaction_template = "ofx_transaction.ofx"

    def __init__(self, account_config: AccountConfig) -> None:
        super().__init__()
        self._account_config = account_config
        self.dtnow = datetime.now().astimezone()
        self._template_reader = Environment(loader=self._make_template_loader())
        self.log.info("Creating ofx client for account %s", self._account)

    def _make_template_loader(self) -> BaseLoader:
        account_type_template_path = self._account_config.account_type.template_path()
        template_paths = [f"templates/{account_type_template_path}", "templates"]
        loaders = [PackageLoader("ofx_converter", path) for path in template_paths]
        loader = ChoiceLoader(loaders)
        return loader

    @property
    def _account(self) -> Account:
        return self._account_config.account

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

    def make_ofx_header(self, transactions: list[Transaction]) -> str:
        self.log.info("Making OFX header for account %s", self._account)
        dtstart = transactions[0].ofx_date
        dtend = transactions[-1].ofx_date
        file_options = self._account_config.file_options
        encoding, charset = file_options.get("encoding"), file_options.get("charset")
        payload = {
            "dtnow": self.ofx_now,
            "dtstart": dtstart,
            "dtend": dtend,
            "fiorg": self._account_config.fiorg,
            "fiid": self._account_config.fiid,
            "bankid": self._account_config.bankid,
            "branchid": self._account_config.branchid,
            "acctid": self._account_config.acctid,
            "accttype": self._account_config.accttype,
            "lang": self._account_config.lang,
            "cur": self._account_config.cur,
            "accttype_abbreviation": self._account_config.account_type.abbreviation(),
            "encoding": encoding,
            "charset": charset,
            "accttype_msgserver": self._account_config.account_type.msg_server(),
        }
        header = self.header_template.render(**payload)
        return header

    def make_ofx_transaction(self, template: Template) -> Callable[[Transaction], str]:
        def inner(t: Transaction) -> str:
            payload = {
                "trn_type": t.transaction_type,
                "dt_posted": t.ofx_date,
                "amount": t.value,
                "desc": t.description,
                "fitid": t.fitid,
            }
            trn_formatted = template.render(**payload)
            return trn_formatted

        return inner

    def make_ofx_transactions(self, transactions: list[Transaction]) -> list[str]:
        self.log.info("Making OFX transactions for account %s", self._account)
        maker = self.make_ofx_transaction(template=self.transaction_template)
        ofx_transactions = list(
            map(
                maker,
                transactions,
            )
        )
        return ofx_transactions

    def make_ofx_footer(self, transactions: list[Transaction]) -> str:
        self.log.info("Making OFX footer for account %s", self._account)
        sorted_transactions = sorted(transactions)
        dtend = sorted_transactions[-1].ofx_date
        last_balance = sorted_transactions[-1].balance
        payload = {
            "last_balance": last_balance,
            "dt_end": dtend,
            "accttype_abbreviation": self._account_config.account_type.abbreviation(),
            "accttype_msgserver": self._account_config.account_type.msg_server(),
        }
        footer = self.footer_template.render(**payload)
        return footer

    def make_ofx_file(self, transactions: list[Transaction]) -> str:
        self.log.info("Making OFX file for account %s", self._account)
        reducer = lambda x, y: x + "\n" + y
        sorted_transactions = sorted(transactions)
        body = reduce(reducer, self.make_ofx_transactions(transactions))
        header = self.make_ofx_header(sorted_transactions)
        footer = self.make_ofx_footer(sorted_transactions)
        total_file = reduce(reducer, [header, body, footer])
        return total_file
