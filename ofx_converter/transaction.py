from datetime import datetime
from typing import Any
from dataclasses import dataclass
from hashlib import md5
from base64 import b64encode
from jinja2 import Template

from ofx_converter.utils import to_ofx_time


@dataclass
class Transaction:
    timestamp: datetime
    description: str
    value: float
    balance: float
    transaction_id: str | None = None

    @property
    def transaction_type(self) -> str:
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

    def make_ofx_transaction(self, template: Template):
        payload = {
            "trn_type": self.transaction_type,
            "dt_posted": self.ofx_date,
            "amount": self.value,
            "desc": self.description,
            "fitid": self.fitid,
        }
        trn_formatted = template.render(**payload)
        return trn_formatted

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Transaction):
            return self.timestamp < other.timestamp
        else:
            raise ValueError(f"Can't compare Transaction to type {type(other)}")
