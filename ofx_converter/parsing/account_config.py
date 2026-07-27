from pathlib import Path
from typing import Any

from ofx_converter.config import get_settings
from ofx_converter.parsing.account_type import AccountType
from ofx_converter.parsing.parser_type import ParserType
from ofx_converter.utils import FileType


class AccountConfig:
    def __init__(self, account_name: str) -> None:
        self._account_name = account_name
        self._settings = get_settings()
        accounts = self._settings.accounts
        if account_name not in accounts:
            raise ValueError(f"Account '{account_name}' not found in settings")
        self._account_settings = accounts[account_name]

    @property
    def account(self) -> str:
        return self._account_name

    @property
    def account_type(self) -> AccountType:
        account_type_str = self._account_settings.account.type
        return AccountType(account_type_str)

    @property
    def parser(self) -> ParserType:
        parser_value = self._account_settings.get("parser")
        if parser_value is not None:
            return ParserType(parser_value)
        if self.file_format == FileType.OFX:
            return ParserType.OFX
        raise ValueError(
            f"Account '{self._account_name}' must specify a parser"
        )

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
