import sys

import pytest

from official_cheater.cli import main


def test_001(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "-e",
            r".\pdf\lower_right__closeout.pdf",
            "--first",
        ],
    )

    main()


def test_002(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "-e",
            r".\pdf\lower_right__closeout.pdf",
            "--last",
        ],
    )

    main()


def test_error_001(monkeypatch):
    """Expect a system.exit(1) on this error"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per_MISSING_FILE.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "-e",
            r".\pdf\lower_right__closeout.pdf",
            "--first",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_error_002(monkeypatch):
    """Expect a system.exit(1) on this error"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per_MISSING_FILE.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "--first",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


def test_error_003(monkeypatch):
    """Expect a system.exit(1) on this error"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per_MISSING_FILE.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "--last",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
