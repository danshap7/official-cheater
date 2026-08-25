import argparse

from .meet import Meet


def run_timeline(args: argparse.Namespace) -> None:
    print(args) if args.debug else None

    m: Meet = Meet(args.input_file)

    if args.merge:
        m.merge_sessions()
