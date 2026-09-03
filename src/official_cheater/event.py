"""tbd."""

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
