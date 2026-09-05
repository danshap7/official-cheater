from dataclasses import dataclass
from itertools import islice

from . import report
from .session import Session
from .utilities import short_event, short_time


@dataclass
class SheetLine:
    womems_ev_num: str = ""
    womens_heat_count: str = ""
    event_name: str = ""
    mens_event_num: str = ""
    mens_heat_count: str = ""
    is_note: bool = False


class CheatSheet:
    def __init__(self, s: Session):
        self.s: Session = s
        self.lines: list[SheetLine] = []

        self._load_session()

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

    def _load_session(self) -> None:

        event_iter = iter(range(len(self.s.events)))

        for i in event_iter:
            # this helps for odd number events in single gender session
            compare_to = (i + 1) if (i + 1) != len(self.s.events) else i

            # is a mix event or a break?
            if self.s.events[i].gender == "Mixed":
                # mixed event
                self._add_line(
                    self.s.events[i].number,
                    self.s.events[i].heat_count,
                    f"{self.s.events[i].distance} Mixed "
                    f"{short_event(self.s.events[i].stroke)}"
                    f"{' R' if self.s.events[i].is_relay else ''}",
                    "",
                    "",
                )

            # single gender session / pool
            elif self.s.events[i].gender == self.s.events[compare_to].gender:
                # left side (female)
                if self.s.events[i].gender in ("Girls", "Women"):
                    self._add_line(
                        self.s.events[i].number,
                        self.s.events[i].heat_count,
                        f"{self.s.events[i].distance} "
                        f"{short_event(self.s.events[i].stroke)}"
                        f"{' R' if self.s.events[i].is_relay else ''}",
                        "",
                        "",
                    )

                else:  # right side (male)
                    self._add_line(
                        "",
                        "",
                        f"{self.s.events[i].distance} "
                        f"{short_event(self.s.events[i].stroke)}"
                        f"{' R' if self.s.events[i].is_relay else ''}",
                        self.s.events[i].number,
                        self.s.events[i].heat_count,
                    )

            elif (self.s.events[i].stroke == self.s.events[i + 1].stroke) and (
                self.s.events[i].distance == self.s.events[i + 1].distance
            ):
                # pair up girls and boys events
                self._add_line(
                    self.s.events[i].number,
                    self.s.events[i].heat_count,
                    f"{self.s.events[i].distance} "
                    f"{short_event(self.s.events[i].stroke)}"
                    f"{' R' if self.s.events[i].is_relay else ''}",
                    self.s.events[i + 1].number,
                    self.s.events[i + 1].heat_count,
                )

                # skip the next index
                next(islice(event_iter, 1, 1), None)

            else:
                # diffent events for each gender
                # eg. 1500 FR for women and 800 for men
                # assumes women before men in this listing
                # TODO - don't assume
                self._add_line(
                    self.s.events[i].number,
                    self.s.events[i].heat_count,
                    f"{self.s.events[i].distance} "
                    f"{short_event(self.s.events[i].stroke)}"
                    f"{' R' if self.s.events[i].is_relay else ''}",
                    "",
                    "",
                )

                self._add_line(
                    "",
                    "",
                    f"{self.s.events[i + 1].distance} "
                    f"{short_event(self.s.events[i + 1].stroke)}"
                    f"{' R' if self.s.events[i + 1].is_relay else ''}",
                    self.s.events[i + 1].number,
                    self.s.events[i + 1].heat_count,
                )

                # skip the next index
                next(islice(event_iter, 1, 1), None)

            # does a break follow the current event?
            if self.s.events[compare_to].break_follows:
                self._add_a_note(
                    f"Break: {self.s.events[compare_to].break_time}-minutes"
                )

        # finish up with the start and end times
        t1: str = short_time(self.s.datetime_start.strftime(report.TIME_FORMAT))
        t2: str = short_time(self.s.datetime_finish.strftime(report.TIME_FORMAT))
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
