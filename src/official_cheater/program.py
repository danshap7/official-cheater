import argparse


def run_program(args: argparse.Namespace) -> None:
    print(args) if args.debug else None
