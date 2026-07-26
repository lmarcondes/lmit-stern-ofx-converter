import re
from datetime import datetime
from decimal import Decimal

from ofxparse.ofxparse import Transaction as OfxTransaction

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser


class OfxTransactionParser(TransactionParser[OfxTransaction]):

    def __init__(self, account: AccountConfig) -> None:
        super().__init__(account)

    def _is_installment(self, memo: str) -> bool:
        patterns = [
            r"Parcela (\d+)/(\d+)",
            r"[ \-](\d+)/(\d+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, memo)
            if match:
                current_installment = match.group(1)
                if int(current_installment) > 1:
                    return True
        return False

    def installment_id(self, tran_id: str, memo: str) -> str | None:
        if self._is_installment(memo):
            return None
        return tran_id

    def parse(self, record: OfxTransaction) -> Transaction | None:
        date: datetime
        desc: str
        value: Decimal
        tran_type: str
        tran_id: str
        (tran_id, date, tran_type, desc, value) = record.id, record.date, record.type, record.memo, record.amount
        transaction = Transaction(
            date,
            desc,
            value,
            transaction_id=self.installment_id(tran_id, desc),
            tran_type=tran_type,
        )
        return transaction
