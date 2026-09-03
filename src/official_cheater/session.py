"""Class to hold session information"""

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
        self.day_of_meet = 0

        self.datetime_start: datetime = field(default_factory=lambda: datetime.now())
        self.datetime_start: datetime = field(default_factory=lambda: datetime.now())

        self.events = []

        # Merging of sessions when you have pools seperated by gender.  This allows
        # both pools' events and heats to be listed on one card.

        # This session's information has been combined into another session
        self.has_been_merged: bool = False

        # This session is the sum/merging of two sessions
        self.merged_session: bool = False

    def add_event(self, e: Event) -> None:
        self.events.append(e)

    def __str__(self):
        return f"S{self.number}\n" + "\n".join(
            "   " + str(event) for event in self.events
        )
