from datetime import timedelta
from re import compile
from typing import Any

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.date_parser import DateParser
from ofx_converter.parsing.money_parser import MoneyParser
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser
from dateutil.relativedelta import relativedelta
from re import compile


class XPTransactionParser(TransactionParser):
    DATE_COL = "Data"
    DESCRIPTION_COL = "Descricao"
    VALUE_COL = "Valor"
    BALANCE_COL = "Saldo"
    INSTALLMENT_COL = "Parcela"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{2})[\\s\\w]+(?P<hour>\\d{2}):(?P<min>\\d{2}):(?P<sec>\\d{2})$"
    _value_pattern = "(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$"

    def __init__(self, account: AccountConfig) -> None:
        super().__init__(account)
        date_regex = compile(self._date_pattern)
        value_regex = compile(self._value_pattern)
        self._money_parser = MoneyParser(account, value_regex)
        self._date_parser = DateParser(date_regex)

    def _parse_installment(
        self, installment_description: str | None
    ) -> tuple[int, int] | None:
        if installment_description is None:
            return

        pattern = compile("(\\d+) de (\\d+)")
        match = pattern.match(installment_description)
        if not match:
            return

        current_installment = match.group(1)
        last_installment = match.group(2)

        return int(current_installment), int(last_installment)

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        (date, desc, value, balance, installment) = (
            record.get(self.DATE_COL),
            record.get(self.DESCRIPTION_COL),
            record.get(self.VALUE_COL),
            record.get(self.BALANCE_COL),
            record.get(self.INSTALLMENT_COL),
        )
        date_parsed = self._date_parser.parse(date)
        value_converted = self._money_parser.parse(value)
        balance_converted = self._money_parser.parse(balance)
        installment_tuple = self._parse_installment(installment)
        if installment_tuple is not None:
            current_installment, _ = installment_tuple
            if current_installment > 1 and date_parsed is not None:
                date_parsed += relativedelta(months=current_installment - 1)
        transaction = Transaction(date_parsed, desc, value_converted, balance_converted)  # type: ignore
        self._log.info(str(transaction))
        if not transaction.is_valid:
            return None
        return transaction


class XPCardTransactionParser(XPTransactionParser):
    DESCRIPTION_COL = "Estabelecimento"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{4})$"
    _value_pattern = "R\\$ (?P<sign>-)?(?P<value>[\\d\\.,]+)$"
