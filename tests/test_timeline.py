import sys

from official_cheater.cli import main


def test_001(monkeypatch):
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
