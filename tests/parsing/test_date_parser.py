import re
from datetime import datetime

from ofx_converter.parsing.date_parser import DateParser
from tests.base_test_case import BaseTestCase


class DateParserTestCase(BaseTestCase):

    def test_parse_xp_full_date(self) -> None:
        date_regex = re.compile(
            "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{2})[\\s\\w]+(?P<hour>\\d{2}):(?P<min>\\d{2}):(?P<sec>\\d{2})$"
        )
        parser = DateParser(date_regex)
        test_cases = [
            (
                "27/11/24 às 12:03:47",
                datetime(
                    year=2024,
                    month=11,
                    day=27,
                    hour=12,
                    minute=3,
                    second=47,
                    tzinfo=parser.timezone,
                ),
            ),
            (
                "04/11/24 às 14:08:19",
                datetime(
                    year=2024,
                    month=11,
                    day=4,
                    hour=14,
                    minute=8,
                    second=19,
                    tzinfo=parser.timezone,
                ),
            ),
            (
                "09/11/24 14:08:19",
                datetime(
                    year=2024,
                    month=11,
                    day=9,
                    hour=14,
                    minute=8,
                    second=19,
                    tzinfo=parser.timezone,
                ),
            ),
            ("09/11/24", None),
            ("04/30/24 às 14:08:19", None),
        ]
        for input, expected in test_cases:
            result = parser.parse(input)
            self.assertEqual(result, expected)

    def test_parse_xp_short_date(self) -> None:
        date_regex = re.compile("^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{4})$")
        parser = DateParser(date_regex)
        test_cases = [
            (
                "07/02/2025",
                datetime(year=2025, month=2, day=7, tzinfo=parser.timezone),
            ),
            (
                "07/12/2025",
                datetime(year=2025, month=12, day=7, tzinfo=parser.timezone),
            ),
            (
                "04/30/2024",
                None,
            ),
        ]
        for input, expected in test_cases:
            result = parser.parse(input)
            self.assertEqual(result, expected)
