from pathlib import Path
from typing import Any

import openpyxl

from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.reader.abstract_reader import BaseReader


class XlsxReader(BaseReader):
    def __init__(
        self,
        sheet_index: int = 0,
        header_row: int | None = None,
        **_: Any
    ) -> None:
        super().__init__()
        self._sheet_index = sheet_index
        self._header_row = header_row

    def read_transactions(
        self, parser: TransactionParser[dict[str, Any]], file_path: Path
    ) -> list[Transaction | None]:
        workbook = openpyxl.load_workbook(
            file_path, data_only=True, read_only=True
        )
        try:
            worksheet = workbook.worksheets[self._sheet_index]
            rows = list(worksheet.iter_rows(values_only=True))
            header_index = self._resolve_header_index(rows)
            header = rows[header_index]
            column_map = {
                str(value): column
                for column, value in enumerate(header)
                if value is not None
            }
            records = (
                {
                    name: row[column] if column < len(row) else None
                    for name, column in column_map.items()
                }
                for row in rows[header_index + 1 :]
            )
            transactions = parser.parse_multiple(records)
        finally:
            workbook.close()
        return transactions

    def _resolve_header_index(self, rows: list[tuple[Any, ...]]) -> int:
        if self._header_row is not None:
            return self._header_row - 1

        required_columns = {"Data", "Valor"}
        for index, row in enumerate(rows):
            string_values = {
                str(value) for value in row if value is not None
            }
            if required_columns <= string_values:
                return index

        raise ValueError(
            "Could not find header row containing 'Data' and 'Valor'"
        )
