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
    return parser
