import sys

import pytest

from official_cheater import debug
from official_cheater.cli import main


def test_001(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["official-cheater", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0


def test_002(monkeypatch):
    """Tests basic debugging features."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["official-cheater", "--debug", "timeline", r".\tests\timeline_001.pdf"],
    )

    main()


def test_00(monkeypatch):

    debug.set(True)
    debug.log("Debug enabled as expected")

    debug.set(False)
    debug.log("ERROR - this should not print")
