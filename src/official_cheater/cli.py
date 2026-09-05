"""Handles command-line arguements for the official-cheater set of tools."""

import argparse
from pathlib import Path

from official_cheater import debug

from .pdf import run_pdf
from .program import run_program
from .stamp import run_stamp
from .timeline import run_timeline
from .watch import run_watchers


def build_stamp_parser(subparsers):
    """Build command-line options for stamp tools.

    Args:
        subparsers: Argument parser subparsers to which the stamp options
            are added.
    """
    parser = subparsers.add_parser("stamp", help="Merge PDF files together")
    parser.add_argument(
        "base_file",
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

    parser.add_argument(
        "--print",
        action="store_true",
        help="Print file to default printer",
    )

    parser.set_defaults(func=run_stamp)


def build_timeline_parser(subparsers):
    """Build command-line options for timeline tools.

    Args:
        subparsers: Argument parser subparsers to which the timeline options
            are added.
    """
    parser = subparsers.add_parser("timeline", help="Analyze timeline")

    parser.add_argument("input_file", type=Path, help="Session report to be analyzed")

    parser.add_argument(
        "-m",
        "--merge",
        action="store_true",
        help="Find mergeable sessions and merge them for cheatsheet",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="MS Excel report name (default name is <input>+.xls)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--5column",
        dest="cheat_layout",
        action="store_const",
        const="5column",
        help="Five column cheat sheet layout",
    )

    group.add_argument(
        "--3column",
        dest="cheat_layout",
        action="store_const",
        const="3column",
        help="Three column cheat sheet layout",
    )

    # 5 column layout is always the default
    parser.set_defaults(cheat_layout="5column")

    parser.set_defaults(func=run_timeline)


def build_program_parser(subparsers):
    """Build command-line options for meet program tools.

    Args:
        subparsers: Argument parser subparsers to which the meet program options
            are added.
    """
    parser = subparsers.add_parser(
        "program", help="Print meet program with combined heats"
    )
    parser.add_argument("input", type=Path, help="Single column meet program")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Combined heat meet program (default name is <input>+.pdf)",
    )
    parser.set_defaults(func=run_program)


def build_pdf_tools_parser(subparsers):
    """Build command-line options for pdf file processing.

    Args:
        subparsers: Argument parser subparsers to which the meet program options
            are added.
    """
    parser = subparsers.add_parser("pdf", help="PDF file processsing")

    parser.add_argument(
        "-m",
        "--merge",
        nargs="+",
        type=Path,
        help="Merge PDF files by listed name or directory",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively walk any directory adding PDFs",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Merged file output (default name is merge.pdf)",
    )

    parser.set_defaults(func=run_pdf)


def pid_or_all(value: str) -> int | str:
    """Enforce that we either have an 'all' or an int as a type"""
    if value.casefold() == "all":
        return "all"

    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a integer PID number or 'all'"
        ) from exc


def build_watcher_parser(subparsers):
    """Build command-line options for watching file processing.

    Args:
        subparsers: Argument parser subparsers to which the meet program options
            are added.
    """
    parser = subparsers.add_parser(
        "watch", help="Directory watchers for stamping files"
    )

    # non-selected options will be set to None from this mux group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--start",
        type=Path,
        help="Start a series on watchers based on supplied JSON file",
    )

    group.add_argument(
        "--stop",
        nargs="+",
        type=pid_or_all,
        help="Stop all watchers, or selectively by PID ",
    )
    group.add_argument(
        "--status",
        action="store_const",
        const="status",
        help="List all watchers",
    )

    parser.set_defaults(func=run_watchers)


def main():
    """Main function for processing command-line arguements."""

    # "hidden" debug option.  This must be called before the subarguemnt.  Example
    # 'official-cheater --debug timeline'  It will not work if included anywhere else.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--debug",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    parser = argparse.ArgumentParser(description="Hy-Tek Helper", parents=[common])
    subparsers = parser.add_subparsers(dest="command", required=True)

    # argument sub-groups
    build_stamp_parser(subparsers)
    build_timeline_parser(subparsers)
    build_program_parser(subparsers)
    build_pdf_tools_parser(subparsers)
    build_watcher_parser(subparsers)

    args = parser.parse_args()

    debug.set(args.debug)

    # make sure we've set 'func' before attempting to call it
    if hasattr(args, "func"):
        args.func(args)
