from pathlib import Path

from official_cheater.cheat_sheet import CheatSheet
from official_cheater.meet import Meet


def test_001(monkeypatch, request):
    """merge two files - same directory - default name"""

    m: Meet = Meet()
    m.parse_session_report(Path(r".\tests\timeline_001.pdf"))

    c: list[CheatSheet] = []

    for s in m.sessions:
        c.append(CheatSheet())

        c[-1].load_session(s)
        c[-1].dump()


def test_002(monkeypatch, request):
    """merge two files - same directory - default name"""

    m: Meet = Meet()
    m.parse_session_report(Path(r".\tests\timeline_002.pdf"))

    c: list[CheatSheet] = []

    for s in m.sessions:
        c.append(CheatSheet())

        c[-1].load_session(s)
        c[-1].dump()
