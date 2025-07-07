
from enum import Enum


class AccountType(Enum):
    CREDIT_CARD = 'credit-card'
    CHECKING = 'checking'

    @property
    def is_liability(self) -> bool:
        if self.name in ['credit-card']:
            return True
        return False
