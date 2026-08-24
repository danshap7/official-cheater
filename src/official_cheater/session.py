"""TDB."""

from dataclasses import field
from datetime import datetime

from .event import Event


class Session:
    def __init__(self, number: str, name: str):
        self.number: str = number
        self.name = name
        self.day: int = 0
        self.entries: int = 0
        self.heats: int = 0
        self.dayOfMeet = 0

        # has been combined into another session
        self.hasBeenMerged: bool = False

        # is the sum/merging of multiple sessions
        self.mergedSession: bool = False

        self.datetime_start: datetime = field(default_factory=datetime.now)
        self.datetime_finish: datetime = field(default_factory=datetime.now)

        self.events = []

    def add_event(self, e: Event) -> None:
        self.events.append(e)

    def __str__(self):
        return f"S{self.number}\n" + "\n".join(
            "   " + str(event) for event in self.events
        )
