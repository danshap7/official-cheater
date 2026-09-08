import argparse
from pathlib import Path

from .excel import ExcelWorkbook
from .meet import Meet


def run_timeline(args: argparse.Namespace) -> None:
    print(args) if args.debug else None

    m: Meet = Meet(args.input_file)

    # merge sessions when pools split by gender
    if args.merge:
        m.merge_sessions()

    wb: ExcelWorkbook = ExcelWorkbook()

    if args.cheat_layout == "5column":
        wb.make_cheat_sheets(m.sessions)
    else:
        wb.make_cheat_sheets(m.sessions, True)

    wb.make_event_durations(m.sessions)
    wb.make_session_diagnostics(m.sessions)

    if not args.output:
        args.output = Path(args.input_file.with_suffix(".xlsx"))

    wb.write(args.output.name)
