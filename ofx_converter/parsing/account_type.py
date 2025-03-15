
from enum import Enum


class AccountType(Enum):
    CREDIT_CARD = 'credit-card'
    CHECKING = 'checking'

    def is_liability(self) -> bool:
        if self in [self.CREDIT_CARD]:
            return True
        return False
