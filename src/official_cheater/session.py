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
        self.day_of_meet: int = 0
        self.events = []

        self.datetime_start: datetime = field(default_factory=lambda: datetime.now())
        self.datetime_finish: datetime = field(default_factory=lambda: datetime.now())

        self.pool_size: int = 8
        self.interval: int = 30
        self.plus_back_interval: int = 15
        self.last_12U_event: int = 0

        # Merging of sessions when you have pools seperated by gender.  This allows
        # both pools' events and heats to be listed on one card.

        # This session's information has been combined into another session
        self.has_been_merged: bool = False

        # This session is the sum/merging of two sessions
        self.merged_session: bool = False

    def add_event(self, e: Event) -> None:
        e.process_event()

        self.events.append(e)

        if e.is_12U:
            self.last_12U_event = len(self.events) - 1

    def __str__(self):
        return f"S{self.number}\n" + "\n".join(
            "   " + str(event) for event in self.events
        )
