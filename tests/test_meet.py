import sys

from official_cheater.cli import main
from official_cheater.event import Event
from official_cheater.meet import Meet
from official_cheater.session import Session


def test_000(monkeypatch, request):

    e: Event = Event()
    e.number = 6
    e.age_group = "10&U"
    e.distance = 1650
    e.stroke = "Freestype"

    s: Session = Session("6", "final sessions")
    s.events.append(e)

    m: Meet = Meet()
    m.sessions.append(s)

    print(e)
    print(s)
    print(m)


def test_001(monkeypatch, request):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "timeline",
            r".\tests\timeline_001.pdf",
        ],
    )

    main()
