from pathlib import Path
from typing import Any

from ofx_converter.config import get_settings
from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_type import AccountType
from ofx_converter.utils import FileType


class AccountConfig:
    def __init__(self, account: Account) -> None:
        self._account = account
        self._settings = get_settings()
        self._account_settings = self._settings["accounts"][account.value]

    @property
    def account(self) -> Account:
        return self._account

    @property
    def account_type(self) -> AccountType:
        account_type_str = self._account_settings.account.type
        account_type = AccountType(account_type_str)
        return account_type

    @property
    def file_format(self) -> FileType:
        return FileType(self._account_settings["files"]["format"])

    @property
    def file_options(self) -> dict[str, Any]:
        return self._account_settings["files"]["options"]

    @property
    def file_in(self) -> Path:
        return Path(self._account_settings["files"]["in"])

    @property
    def file_out(self) -> Path:
        return Path(self._account_settings["files"]["out"])

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
    def branchid(self) -> str | None:
        return self._account_settings["account"].get("branch")

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
