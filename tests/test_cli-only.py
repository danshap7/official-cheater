import sys

import pytest

from official_cheater.cli import main


def test_001(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["official-cheater", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
