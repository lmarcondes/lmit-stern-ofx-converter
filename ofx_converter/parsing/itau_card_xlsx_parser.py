from datetime import date, datetime
from decimal import Decimal
from re import compile
from typing import Any
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser


class ItauCardXlsxParser(TransactionParser[dict[str, Any]]):
    DATE_COL = "Data"
    DESCRIPTION_COL = "Lançamento"
    INSTALLMENT_COL = "Parcelamento"
    VALUE_COL = "Valor"

    _installment_pattern = compile(r"(\d+) de (\d+)")
    _timezone = ZoneInfo("America/Sao_Paulo")

    def __init__(self, account: AccountConfig) -> None:
        super().__init__(account)

    def _parse_installment(
        self, installment_description: str | None
    ) -> tuple[int, int] | None:
        if installment_description is None:
            return None

        match = self._installment_pattern.search(installment_description)
        if not match:
            return None

        return int(match.group(1)), int(match.group(2))

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        date_value = record.get(self.DATE_COL)
        description = record.get(self.DESCRIPTION_COL)
        installment = record.get(self.INSTALLMENT_COL)
        value_raw = record.get(self.VALUE_COL)

        if date_value is None or description is None or value_raw is None:
            return None

        date_parsed = self._ensure_datetime(date_value)
        value_converted = Decimal(str(value_raw)).quantize(Decimal("0.01"))
        if self._account_config.account_type.is_liability:
            value_converted = -value_converted

        description_text = str(description)
        installment_tuple = self._parse_installment(installment)
        if installment_tuple is not None:
            current_installment, _ = installment_tuple
            description_text = f"{description_text} - {installment}"
            if current_installment > 1:
                date_parsed += relativedelta(months=current_installment - 1)

        transaction = Transaction(
            date_parsed,
            description_text,
            value_converted,
        )
        self._log.info(str(transaction))
        if not transaction.is_valid:
            return None
        return transaction

    def _ensure_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            raise ValueError(f"Unexpected date value: {value!r}")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self._timezone)
        return dt
