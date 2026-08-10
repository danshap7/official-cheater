import argparse
from pathlib import Path

from .program import run_program
from .stamp import run_stamp
from .timeline import run_timeline


def build_stamp_parser(subparsers):
    parser = subparsers.add_parser("stamp", help="Merge PDF files together")
    parser.add_argument(
        "-b",
        "--base",
        required=True,
        type=Path,
        help="PDF onto which the overlay files are applied",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output name of stampped files",
    )

    parser.add_argument(
        "-a",
        "--overlay_all",
        nargs="+",
        type=Path,
        required=True,
        help="Space-separated list of overlay PDFs for all pages",
    )

    parser.add_argument(
        "-e",
        "--overlay_event",
        nargs="+",
        type=Path,
        help="Space-separated list of overlay PDFs per event",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--first",
        dest="event_stamp",
        action="store_const",
        const="first",
        help="Stamp at the first page of the event",
    )

    group.add_argument(
        "--last",
        dest="event_stamp",
        action="store_const",
        const="last",
        help="Stamp at the last page of the event",
    )

    parser.set_defaults(func=run_stamp)


def build_timeline_parser(subparsers):
    parser = subparsers.add_parser("timeline", help="Analyze timeline")
    parser.add_argument(
        "-i", "--input", required=True, type=Path, help="Session report to be analyzed"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="MS Excel report name (default name is <input>+.xls)",
    )
    parser.set_defaults(func=run_timeline)


def build_program_parser(subparsers):
    parser = subparsers.add_parser(
        "program", help="Print meet program with combined heats"
    )
    parser.add_argument(
        "-i", "--input", required=True, type=Path, help="Single column meet program"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Combined heat meet program (default name is <input>+.pdf)",
    )
    parser.set_defaults(func=run_program)


def main():
    parser = argparse.ArgumentParser(description="Hy-Tek Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # argument sub-groups
    build_stamp_parser(subparsers)
    build_timeline_parser(subparsers)
    build_program_parser(subparsers)

    args = parser.parse_args()

    # make sure we've set 'func' before attempting to call it
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
