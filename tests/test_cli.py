from click.testing import CliRunner

from ofx_converter import main
from tests.base_test_case import BaseTestCase


class TestCliSummary(BaseTestCase):
    def test_convert_reports_failures_and_exits_nonzero(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "convert",
                "nubank-cartao-with-failure",
                "--from_date",
                "2025-01",
                "--to_date",
                "2025-12",
            ],
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Failed", result.output)
        self.assertIn("2025-06-broken.ofx", result.output)

    def test_convert_exits_zero_on_success(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "convert",
                "nubank-cartao",
                "--from_date",
                "2025-01",
                "--to_date",
                "2025-12",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Converted", result.output)
