"""Tools for processing Hy-Tek Meet Manager Meet Program PDF files."""

import re
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

from . import debug

# Regex for standard head on all reports
# Example:
#     ABC Aquatic Center - Site License HY-TEK's MEET MANAGER 8.0 - 6/22/2026 Page 2
#
# group 1: Licensee (club/facility/organization)
# group 2: Hy-Tek Major version
# group 3: Hy-Tek Minor version
# group 4: Report page number
HEADER: re.Pattern = re.compile(r"(.+)HY - TEK's MEET MANAGER (\d)\.(\d).+(Page \d+)")


# Regex for Event starting text on meet programs
# Example:
#    Event 42 Boys 13-14 200 Yard Medley Relay
# group 1: Event number
EVENT_START: re.Pattern = re.compile(r"^Event\s+(\d+)")


# Regex for event line in a sessoin report (timeline)
# Example:
#     Session: 2 Thursday PM
#
# group 1: Session Number
# group 2: Session Name
SESSION_HEADER = re.compile(r"Session: (\d+[^ ]*)\s(.+)")


# Eample:
#     Finals 5 Women 200 Medley Relay 22 3 u 06:46 PM
#
# group 1: Compitition type (prelim, final, timed final, etc)
# group 2: Event number
# group 3: Gender
# group 4: Age Group (optional)
# group 5: Distance
# group 6: Stroke
# group 7: Relay (optional)
# group 8: Athlete entries
# group 9: Heat count
TIMELINE_EVENT = re.compile(
    r"(Prelims|Finals|Finals-1|Finals-S)\s*"
    r"(\d+).*"
    r"(Girls|Women|Boys|Men|Mixed)\s*"
    r"(\d+ & Under |\d+ & Over |\d+-\d+ )*"
    r"(\d+) "
    r"(Butterfly|Backstroke|Breaststroke|"
    r"Freestyle|Medley|IM)"
    r"( Relay)* "
    r"(\d+)\s*"
    r"(\d+)\s*"
    r"[_]*\s*"
    r"(\d{2}\:\d{2} (?:AM|PM))"
)

# group 1: Minutes for break
TIMELINE_BREAK = re.compile(r"Break: (\d+) Minutes")

# group 1: Athlete count
# group 2: Heat count
TIMELINE_TOTALS = re.compile(r"Entry / Heat Totals: (\d+) (\d+)")

# group 1: Hour
# group 2: Minute
# group 3: Second
# group 4: AM/PM
TIMELINE_START_T = re.compile(
    r"Day of Meet: (\d+)\s+Starts at " r"(\d{2})\:(\d{2})\s?((?:AM|PM))"
)

# group 1: Hour
# group 2: Minute
# group 3: Second
# group 4: AM/PM
TIMELINE_END_T = re.compile(r"Finish Time\D+(\d{2})\:(\d{2})\s(AM|PM)")


# Time format used on reports
TIME_FORMAT = r"%I:%M %p"


def get_event_page_mapping(pdf_file: Path) -> dict[int, list[int]]:
    """Map the event number to a page in the 'pdf_file'.  The meet program
    passed in must be single column and one event per page.

    Args:
        pdf_file: PDF file path and name
    """
    reader = PdfReader(pdf_file)

    ev_mapping: dict[int, list[int]] = defaultdict(list)
    current_ev_num: int = 0

    # loop through each page in the PDF report
    for page_num, page in enumerate(reader.pages, start=0):
        new_ev: bool = False

        page_list: list[str] = page.extract_text().splitlines()

        # loop through each line in the page
        for line in page_list:
            if match := EVENT_START.search(line):
                new_ev = True
                current_ev_num = int(match.group(1))
                ev_mapping[current_ev_num].append(page_num)

        if not new_ev:
            # this was a continuation page
            ev_mapping[current_ev_num].append(page_num)

    return ev_mapping


def cleanup_line(line: str) -> str:
    """Clean up issues in text recognization we've come across.

    Args:
        line: single line read from PdfReader

    Return
        Cleaned up line
    """
    if debug.is_set():
        # handle possible ligatures with the FL in fly
        # this issues has only showed up in one session report
        if re.search(r"ϐly", line):
            print("\tFixing Bufferfly ligature")

        # handle space between B*oys
        if re.search(r"B oys", line):
            print("\tFixing space in gender - Boys")

        # handle space between Gi*rls
        if re.search(r"Gi rls", line):
            print("\tFixing space in gender - Girls")

    line = re.sub(r"ϐly", r"fly", line)
    line = re.sub(r"B oys", r"Boys", line)
    line = re.sub(r"Gi rls", r"Girls", line)

    return line
