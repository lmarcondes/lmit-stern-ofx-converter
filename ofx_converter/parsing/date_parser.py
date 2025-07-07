import re
from datetime import datetime
from traceback import print_exc
from zoneinfo import ZoneInfo

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.abstract_value_parser import StringParser


class DateParser(LogMixin, StringParser[datetime]):
    _default_timezone = ZoneInfo("America/Sao_Paulo")

    def __init__(
        self, date_regex: re.Pattern[str], timezone: ZoneInfo = _default_timezone
    ) -> None:
        super().__init__()
        self._date_regex = date_regex
        self._timezone = timezone

    @property
    def timezone(self) -> ZoneInfo:
        return self._timezone

    def parse(self, input: str | None) -> datetime | None:
        if input is None:
            return None
        date_obj = self._date_regex.match(input)
        if date_obj is None:
            return None
        date_string = self.make_iso_string(**date_obj.groupdict())
        try:
            date_converted = datetime.fromisoformat(date_string)
            date_converted = date_converted.replace(tzinfo=self.timezone)
        except ValueError:
            print_exc()
            self.log.error("Failed converting date %s, returning None", date_string)
            return None
        return date_converted

    @staticmethod
    def _adjust_year(year: str | int) -> str:
        len_year = len(str(year))
        if len_year == 4:
            return str(year)
        elif len_year == 2:
            current_century = datetime.now().year // 100
            past_century = current_century - 1
            prefix = current_century if int(year) < 50 else past_century
            adjusted_year = f"{prefix}{year}"
            return adjusted_year
        else:
            raise ValueError("Invalid year %s", year)

    def make_iso_string(self, **match_dict: str) -> str:
        defaults = dict(month="01", day="01", hour="00", min="00", sec="00")
        values = {**defaults, **match_dict}
        values["year"] = self._adjust_year(values["year"])
        date_string = "{year}-{month}-{day}T{hour}:{min}:{sec}.000".format(**values)
        return date_string
