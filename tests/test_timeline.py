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


def test_002(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "timeline",
            r".\tests\timeline_002.pdf",
        ],
    )

    main()


def test_003(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "--debug",
            "timeline",
            r".\tests\timeline_003_staggered_events-ligature_issue_in_fly.pdf",
        ],
    )

    main()


def test_004(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "--debug",
            "timeline",
            r".\tests\timeline_004_has_spaces_between_genders.pdf",
        ],
    )

    main()


def test_005(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "timeline",
            "--merge",
            r".\tests\timeline_001.pdf",
        ],
    )

    main()
