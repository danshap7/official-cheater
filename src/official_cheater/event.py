"""tbd."""

import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event:
    """Holds variables associated with a single swim event."""

    comp_type: str = ""
    number: int = 0
    gender: str = ""
    age_group: str = ""
    distance: int = 0
    stroke: str = ""
    total_entries: int = 0
    heat_count: int = 0
    is_relay: bool = False
    is_12U: bool = False
    datetime_start: datetime = field(default_factory=lambda: datetime.now())

    # if a break follows this event on the session report
    break_follows: bool = False
    break_time: int = 0

    def attachBreak(self, t: int) -> None:
        """Tbd."""
        self.break_time = t
        self.break_follows = True

    def __str__(self):
        return f"E{self.number} {self.age_group} {self.distance} {self.stroke}"

    def process_event(self) -> None:
        self._setTwelveAndUnder()

    def _setTwelveAndUnder(self) -> None:
        """Flags whether a session is considered a 12U session

        Is a 12&U event per 205.3.1F (4 hour rule)
        https://www.usaswimming.org/docs/default-source/officialsdocuments/
        officials-training-resources/interpretations-and-recommendations/
        interpretation-of-four-hour-rule-10-25-16.pdf

        The rule does NOT apply to Open events even if swimmers 12 years of
        age or younger are entered.

        But, 'Events that are scored multi-age are impacted by the rule if
        the multi-age scoring involves 12U'
        """

        UPPER_AGE = 12

        lower_age: int = 0
        upper_age: int = 100

        if self.age_group is not None:
            if group := re.search(r"(\d+) & Under", self.age_group):
                upper_age: int = int(group.group(1))

            elif group := re.search(r"(\d+) & Over", self.age_group):
                lower_age: int = int(group.group(1))

            elif group := re.search(r"(\d+)-(\d+)", self.age_group):
                lower_age: int = int(group.group(1))
                upper_age: int = int(group.group(2))

            self.is_12U = lower_age <= UPPER_AGE or upper_age <= UPPER_AGE
