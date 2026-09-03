"""Tbd."""

from copy import copy
from datetime import datetime
from itertools import islice
from pathlib import Path
from typing import Final

from pypdf import PdfReader

from . import debug, report
from .event import Event
from .session import Session


class Meet:
    _PRELIM_RE: Final[str] = "prelim"
    _FINAL_RE: Final[str] = "final"

    def __init__(self, filename: str):
        self.debug: bool = debug.is_set()
        self.sessions: list[Session] = []
        self.filename: Path = Path(filename)

        self._parse_session_report()

    def _parse_session_report(self):
        reader = PdfReader(self.filename)

        # flag handles long sessions that span more than one page
        new_session_start: bool = True

        print(f"\nProcessing {self.filename}:")

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

                    start_time: datetime = datetime.strptime(
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
                    )

                # session end time
                elif match := report.TIMELINE_END_T.search(line):
                    self.sessions[-1].datetime_finish = datetime.strptime(
                        f"{match.group(1)}:{match.group(2)} {match.group(3)}",
                        report.TIME_FORMAT,
                    )

                    # "Finish Time" is always at the end of a session.  The
                    #  next line read will be the beginning of a new session.
                    #  This helps handle cases where the session timeline spans
                    # multiple pages
                    new_session_start = True

    def merge_sessions(self):
        """Find mergeable sessions and adds a merged version"""
        sessions_itr = iter(range(len(self.sessions) - 1))
        for i in sessions_itr:
            matching = True

            # do the event counts between sessionss match?
            if len(self.sessions[i].events) == len(self.sessions[i + 1].events):
                # make sure we're not comparing prelims to finals
                if (
                    "prelim" in self.sessions[i].name
                    and "final" in self.sessions[i + 1].name
                ):
                    continue

                # Closer, lets compare all event names and distances
                matching = all(
                    event1.stroke == event2.stroke
                    and event1.distance == event2.distance
                    for (event1, event2) in zip(
                        self.sessions[i].events, self.sessions[i + 1].events
                    )
                )

                # done comparing each event
                if matching:
                    print(
                        f">> Merging sessions {self.sessions[i].number} "
                        f"and {self.sessions[i + 1].number}"
                    )

                    self._merge_the_sessions(i, i + 1)

                    # we have a matching pair i and i+1
                    # we don't need to compare i+1 and i+2
                    next(islice(sessions_itr, 1, 1), None)

    def _merge_the_sessions(self, s1_index: int, s2_index: int) -> None:
        """Adds merged version of the two sessions to self.sessions.  The original
        sessions will be kept, but flagged as being merged
        """
        s1: Session = self.sessions[s1_index]
        s2: Session = self.sessions[s2_index]

        # make new combined session
        # merged number: (session one) number "+"
        # merged name: session one name and session two name
        new_session: Session = Session(
            s1.number + "+",
            s1.name + s2.name,
        )

        # flag as a merged session
        new_session.merged_session = True

        new_session.day = s1.day
        new_session.entries = s1.entries + s2.entries
        new_session.heats = s1.heats + s2.heats
        new_session.day_of_meet = s1.day_of_meet

        # assuming these start at the same time
        new_session.datetime_start = s1.datetime_start

        # pick the later of the two end times
        new_session.datetime_finish = max(
            s1.datetime_finish,
            s2.datetime_finish,
        )

        for event1, event2 in zip(s1.events, s2.events):
            new_session.events.append(copy(event1))
            new_session.events.append(copy(event2))

        # mark the original sessions as merged
        s1.has_been_merged = True
        s2.has_been_merged = True

        # insert new merged event before original events
        self.sessions.insert(s1_index, new_session)

    def __str__(self):
        return "Meet\n" + "\n".join(" " + str(session) for session in self.sessions)
