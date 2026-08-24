"""Tbd."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pypdf import PdfReader

from . import debug, report
from .event import Event
from .session import Session


class Meet:
    def __init__(self):
        self.debug: bool = debug.is_set()
        self.sessions: list[Session] = []

    def parse_session_report(self, filename: Path):
        reader = PdfReader(filename)

        # flag handles long sessions that span more than one page
        new_session_start: bool = True

        print(f"\nProcessing {filename}:")

        # for each page
        for page in reader.pages:
            # get a list of strings
            page_lines: list[str] = page.extract_text().splitlines()

            for line in page_lines:
                print(f">> {line}") if self.debug else None  # DEBUG

                line = report.cleanup_line(line)

                if match := report.SESSION_HEADER.search(line):
                    number: str = match.group(1)
                    name: str = match.group(2)

                    # Test whether we are continuing the session from
                    # the previous page.
                    if new_session_start:
                        self.sessions.append(Session(number, name))
                        new_session_start = False

                # capture every event listed for the session
                elif match := report.TIMELINE_EVENT.search(line):
                    print("NEW EVENT") if self.debug else None  # DEBUG

                    start_time: datetime = datetime.strptime(  # noqa: DTZ007
                        f"{match.group(10)}", report.TIME_FORMAT
                    )

                    self.sessions[-1].add_event(
                        Event(
                            comp_type=match.group(1),
                            number=int(match.group(2)),
                            gender=match.group(3),
                            age_group=match.group(4),
                            distance=int(match.group(5)),
                            stroke=match.group(6),
                            total_entries=int(match.group(8)),
                            heat_count=int(match.group(9)),
                            is_relay=match.group(7) is not None,
                            datetime_start=start_time,
                        )
                    )

                # capture breaks in the timeline
                elif match := report.TIMELINE_BREAK.search(line):
                    self.sessions[-1].events[-1].attachBreak(match.group(1))

                # athlete and heat counts
                elif match := report.TIMELINE_TOTALS.search(line):
                    self.sessions[-1].entries = int(match.group(1))
                    self.sessions[-1].heats = int(match.group(2))

                # session start time
                elif match := report.TIMELINE_START_T.search(line):
                    self.sessions[-1].datetime_start = datetime.strptime(
                        f"{match.group(2)}:{match.group(3)} {match.group(4)}",
                        report.TIME_FORMAT,
                    ).replace(tzinfo=ZoneInfo("America/Phoenix"))

                # session end time
                elif match := report.TIMELINE_END_T.search(line):
                    self.sessions[-1].datetime_finish = datetime.strptime(
                        f"{match.group(1)}:{match.group(2)} {match.group(3)}",
                        report.TIME_FORMAT,
                    ).replace(tzinfo=ZoneInfo("America/Phoenix"))

                    # "Finish Time" is always at the end of a session.  The
                    #  next line read will be the beginning of a new session.
                    #  This helps handle cases where the session timeline spans
                    # multiple pages
                    new_session_start = True

    def __str__(self):
        return "Meet\n" + "\n".join(" " + str(session) for session in self.sessions)
