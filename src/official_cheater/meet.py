"""Tbd."""

from pypdf import PageObject, PdfReader, PdfWriter
from pathlib import Path
from . import report


class Meet:

    def __init__(self):
        self.session = []
        self.debug: bool = False

    def parseSessionReport(self, filename: Path, enableDebug=False):
        reader = PdfReader(filename)

        self.debug = enableDebug

        # flag handles long sessions that span more than one page
        startOfNewSession: bool = True

        print(f"\nProcessing {filename}:")

        # for each page
        for page in reader.pages:

            # get a list of strings
            page_lines: list[str] = page.extract_text().splitlines()

            for line in page_lines:

                print(f">> {line}") if self.debug else None  # DEBUG

                line = report.cleanup_line(line)


"""
                # new session
                if group := re.search(r"Session: (\d+[^ ]*)\s(.+)", pageLine):

                    currentNumber = group.group(1)
                    currentName = group.group(2)

                    # test whether we are continuing the session from
                    # the previous page
                    if startOfNewSession:
                        self.session.append(Session(currentNumber, currentName))
                        startOfNewSession = False

                    print(f"   Page {i+1}, Session {currentNumber}")

                if evMatch := re.search(eventRe, pageLine):

                    print("NEW EVENT") if self.debug else None  # DEBUG

                    startT: datetime = datetime.strptime(
                        f"{evMatch.group(10)}", timeFormat
                    )

                    self.session[-1].addEvent(
                        Event(
                            evMatch.group(1),
                            evMatch.group(2),
                            evMatch.group(3),
                            evMatch.group(4),
                            evMatch.group(5),
                            evMatch.group(6),
                            evMatch.group(8),
                            evMatch.group(9),
                            evMatch.group(7) is not None,
                            startT,
                        )
                    )

                elif evMatch := re.search(r"Break: (\d+) Minutes", pageLine):

                    self.session[-1].event[-1].attachBreak(evMatch.group(1))

                elif evMatch := re.search(
                    r"Entry / Heat Totals: (\d+) (\d+)", pageLine
                ):
                    self.session[-1].entries = evMatch.group(1)
                    self.session[-1].heats = evMatch.group(2)

                elif evMatch := re.search(
                    r"Day of Meet: (\d+)\s+Starts at "
                    r"(\d{2})\:(\d{2})\s?((?:AM|PM))",
                    pageLine,
                ):

                    self.session[-1].datetimeStart = datetime.strptime(
                        f"{evMatch.group(2)}"
                        f":{evMatch.group(3)}"
                        f" {evMatch.group(4)}",
                        timeFormat,
                    )

                elif evMatch := re.search(
                    r"Finish Time\D+(\d{2})\:(\d{2})\s(AM|PM)", pageLine
                ):

                    self.session[-1].datetimeFinish = datetime.strptime(
                        f"{evMatch.group(1)}:"
                        f"{evMatch.group(2)} "
                        f"{evMatch.group(3)}",
                        timeFormat,
                    )

                    # "Finish Time" is always at the end of a session
                    # The next line read will be the beginning of a new session
                    startOfNewSession = True

                else:
                    pass
"""

if __name__ == "__main__":
    pass
