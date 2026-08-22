import argparse

from .meet import Meet


def run_timeline(args: argparse.Namespace) -> None:
    print(args) if args.debug else None

    m: Meet = Meet()

    m.parse_session_report(args.input_file)
