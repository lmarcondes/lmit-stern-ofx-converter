from base64 import b64encode
from datetime import datetime
from decimal import Decimal
from functools import cached_property, reduce
from hashlib import md5
from typing import Any, Callable

from ofx_converter.utils import to_ofx_time


class Transaction:
    def __init__(
        self,
        timestamp: datetime,
        description: str,
        value: Decimal | float,
        balance: Decimal | None = None,
        transaction_id: str | None = None,
        tran_type: str | None = None,
    ) -> None:
        self.timestamp = timestamp
        self.description = description
        self._value = value
        self._balance = balance
        self.transaction_id = transaction_id
        self._tran_type = tran_type

    @cached_property
    def value(self) -> Decimal:
        return Decimal(self._value).quantize(Decimal("0.01"))

    @cached_property
    def balance(self) -> Decimal | None:
        balance = self._balance
        if balance is None:
            return None
        return balance.quantize(Decimal("0.01"))

    @property
    def _has_valid_tran_type(self) -> bool:

        if self._tran_type is not None:
            value = self.value
            tran_type = self._tran_type
            valid = (value >= 0 and tran_type.lower() == "credit") or (
                value <= 0 and tran_type.lower() == "debit"
            )
            return valid
        else:
            return True

    @cached_property
    def transaction_type(self) -> str:
        if self._tran_type is not None:
            if not self._has_valid_tran_type:
                raise ValueError(
                    "Incompatible transction type %s with amount %s",
                    self._tran_type,
                    self.value,
                )
            return self._tran_type
        else:
            return "DEBIT" if self.value < 0 else "CREDIT"

    @property
    def ofx_date(self) -> str:
        return to_ofx_time(self.timestamp)

    @property
    def fitid(self) -> str:
        if self.transaction_id is not None:
            return self.transaction_id
        key = "-".join(
            map(
                lambda x: str(x),
                [self.timestamp.isoformat(), self.description, self.value],
            )
        )
        digest = b64encode(md5(key.encode()).digest()).decode()
        return digest

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Transaction):
            return self.timestamp < other.timestamp
        else:
            raise ValueError(f"Can't compare Transaction to type {type(other)}")

    def __str__(self) -> str:
        return f"Transaction(date:{self.timestamp},desc:{self.description},value:{self.value})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def is_valid(self) -> bool:
        valid_conversions = map(
            lambda x: x is not None, [self.timestamp, self.description, self.value]
        )
        reducer: Callable[[bool, bool], bool] = lambda x, y: x and y
        is_valid_transaction = reduce(reducer, valid_conversions)
        return is_valid_transaction
