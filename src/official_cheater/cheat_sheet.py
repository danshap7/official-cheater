from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path

from . import report
from .meet import Meet
from .session import Session


@dataclass
class SheetLine:
    womems_ev_num: str = ""
    womens_heat_count: str = ""
    event_name: str = ""
    mens_event_num: str = ""
    mens_heat_count: str = ""
    is_note: bool = False


@dataclass
class CheatSheet:
    lines: list[SheetLine] = field(default_factory=list)
    s: Session | None = None

    @staticmethod
    def short_time(time: str) -> str:

        # remove leading zeros
        time = time.lstrip("0")

        # swap A for AM and P for PM
        time = time.replace(" AM", "A")
        time = time.replace(" PM", "P")

        return time

    @staticmethod
    def short_event(eventname: str) -> str | None:

        lookup: dict[str, str] = {
            "Butterfly": "Fly",
            "Backstroke": "BK",
            "Breaststroke": "BR",
            "Freestyle": "FR",
            "Medley": "Med",
            "IM": "IM",
        }

        # returns None if eventname is not found
        return lookup.get(eventname)

    @staticmethod
    def short_gender(gender: str) -> str | None:

        lookup: dict[str, str] = {
            "Girls": "W",
            "Women": "W",
            "Boys": "M",
            "Men": "M",
            "Mixed": "X",
        }

        # returns None if gender is not found
        return lookup.get(gender)

    def _add_line(
        self,
        womems_ev_num,
        womens_heat_count,
        event_name,
        mens_event_num,
        mens_heat_count,
    ) -> None:

        s: SheetLine = SheetLine(
            womems_ev_num,
            womens_heat_count,
            event_name,
            mens_event_num,
            mens_heat_count,
        )
        self.lines.append(s)

    def _add_a_note(self, note) -> None:
        s = SheetLine(event_name=note, is_note=True)
        self.lines.append(s)

    def load_session(self, s: Session) -> None:

        self.s = s

        event_iter = iter(range(len(s.events)))

        for i in event_iter:
            # this helps for odd number events in single gender session
            compare_to = (i + 1) if (i + 1) != len(s.events) else i

            # is a mix event or a break?
            if s.events[i].gender == "Mixed":
                # mixed event
                self._add_line(
                    s.events[i].number,
                    s.events[i].heat_count,
                    f"{s.events[i].distance} Mixed "
                    f"{CheatSheet.short_event(s.events[i].stroke)}"
                    f"{' R' if s.events[i].is_relay else ''}",
                    "",
                    "",
                )

            # single gender session / pool
            elif s.events[i].gender == s.events[compare_to].gender:
                # left side (female)
                if s.events[i].gender in ("Girls", "Women"):
                    self._add_line(
                        s.events[i].number,
                        s.events[i].heat_count,
                        f"{s.events[i].distance} "
                        f"{CheatSheet.short_event(s.events[i].stroke)}"
                        f"{' R' if s.events[i].is_relay else ''}",
                        "",
                        "",
                    )

                else:  # right side (male)
                    self._add_line(
                        "",
                        "",
                        f"{s.events[i].distance} "
                        f"{CheatSheet.short_event(s.events[i].stroke)}"
                        f"{' R' if s.events[i].is_relay else ''}",
                        s.events[i].number,
                        s.events[i].heat_count,
                    )

            elif (s.events[i].stroke == s.events[i + 1].stroke) and (
                s.events[i].distance == s.events[i + 1].distance
            ):
                # pair up girls and boys events
                self._add_line(
                    s.events[i].number,
                    s.events[i].heat_count,
                    f"{s.events[i].distance} "
                    f"{CheatSheet.short_event(s.events[i].stroke)}"
                    f"{' R' if s.events[i].is_relay else ''}",
                    s.events[i + 1].number,
                    s.events[i + 1].heat_count,
                )

                # skip the next index
                next(islice(event_iter, 1, 1), None)

            else:
                # diffent events for each gender
                # eg. 1500 FR for women and 800 for men
                # assumes women before men in this listing
                # TODO - don't assume
                self._add_line(
                    s.events[i].number,
                    s.events[i].heat_count,
                    f"{s.events[i].distance} "
                    f"{CheatSheet.short_event(s.events[i].stroke)}"
                    f"{' R' if s.events[i].is_relay else ''}",
                    "",
                    "",
                )

                self._add_line(
                    "",
                    "",
                    f"{s.events[i + 1].distance} "
                    f"{CheatSheet.short_event(s.events[i + 1].stroke)}"
                    f"{' R' if s.events[i + 1].is_relay else ''}",
                    s.events[i + 1].number,
                    s.events[i + 1].heat_count,
                )

                # skip the next index
                next(islice(event_iter, 1, 1), None)

            # does a break follow the current event?
            if s.events[compare_to].break_follows:
                self._add_a_note(f"Break: {s.events[compare_to].break_time}-minutes")

        # finish up with the start and end times
        t1: str = CheatSheet.short_time(s.datetime_start.strftime(report.TIME_FORMAT))
        t2: str = CheatSheet.short_time(s.datetime_finish.strftime(report.TIME_FORMAT))
        self._add_a_note(f"Start: {t1} Finish: {t2}")

    def dump(self):

        if self.s is not None:
            print(f"session {self.s.number}: {self.s.name}")

        for i in self.lines:
            print(
                f"{i.womems_ev_num}\\{i.womens_heat_count}\
            {i.event_name}\
            {i.mens_event_num}\\{i.mens_heat_count}"
            )


if __name__ == "__main__":
    # Delete me sooon
    # this is for initial test

    m: Meet = Meet()
    m.parse_session_report(Path(r".\tests\timeline_002.pdf"))

    c: list[CheatSheet] = []

    for s in m.sessions:
        c.append(CheatSheet())

        c[-1].load_session(s)
        c[-1].dump()
