
from enum import Enum


class AccountType(Enum):
    CREDIT_CARD = 'credit-card'
    CHECKING = 'checking'

    @property
    def is_liability(self) -> bool:
        if self in [AccountType.CREDIT_CARD]:
            return True
        return False

    def abbreviation(self) -> str:
        if self == AccountType.CREDIT_CARD:
            return "CC"
        elif self == AccountType.CHECKING:
            return "BANK"
        else:
            raise NotImplementedError()

    def msg_server(self) -> str:
        if self == AccountType.CREDIT_CARD:
            return "CREDITCARD"
        elif self == AccountType.CHECKING:
            return "BANK"
        else:
            raise NotImplementedError()
