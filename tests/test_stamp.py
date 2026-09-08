import sys

import pytest

from official_cheater.cli import main


def test_001(monkeypatch):
    """Stamp one file on every page, one per event on the first event page"""
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
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_all-event-first_STAMPED.pdf",
        ],
    )

    main()


def test_002(monkeypatch):
    """Stamp one file on every page, one per event on the last event page"""
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
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_all-event-last_STAMPED.pdf",
        ],
    )

    main()


def test_003(monkeypatch):
    """Stamp one file on every page, one per event on the default (first) event page"""
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
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_all-event-default_STAMPED.pdf",
        ],
    )

    main()


def test_004(monkeypatch):
    """Stamp one file on every page"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_all_STAMPED.pdf",
        ],
    )

    main()


def test_005(monkeypatch):
    """Stamp two files on every page"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
            r".\pdf\lower_right__closeout.pdf",
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_all_2files_STAMPED.pdf",
        ],
    )

    main()


def test_006(monkeypatch):
    """Stamp one file on every event - no all option"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-e",
            r".\pdf\lower_right__closeout.pdf",
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_event_1files_STAMPED.pdf",
        ],
    )

    main()


def test_007(monkeypatch):
    """Stamp two files on every event - no all option"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-e",
            r".\pdf\lower_right__closeout.pdf",
            r".\pdf\upper_right__order_of_finish.pdf",
            "--output",
            r".\tests\meet_progam_single_column_one_event_per_TEST_event_2files_STAMPED.pdf",
        ],
    )

    main()


def test_008(monkeypatch):
    """Stamp one file every page with default output"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "official-cheater",
            "stamp",
            r".\tests\meet_progam_single_column_one_event_per.pdf",
            "-a",
            r".\pdf\upper_right__order_of_finish.pdf",
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
