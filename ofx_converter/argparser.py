from argparse import ArgumentParser


def get_main_parser() -> ArgumentParser:
    parser = ArgumentParser(
            prog="ofx-converter",
            description="Convert csv to OFX",
            )
    parser.add_argument(
            "--account",
            action="store",
            type=str,
            required=True
            )
    parser.add_argument(
            "--from_date",
            action="store",
            type=str,
            required=False,
            default=None
            )
    parser.add_argument(
            "--to_date",
            action="store",
            type=str,
            required=False,
            default=None
            )
    return parser
