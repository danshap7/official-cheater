from datetime import datetime, timedelta

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from .cheat_sheet import CheatSheet
from .meet import Meet
from .session import Session

# excel worksheet board style
_THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

# excel worksheet font style
_FONT_STYLE = Font(size="14")
_FONT_STYLE_BOLD = Font(size="14", bold=True)

# excel worksheet column widths
_EVENT_COLUMN_WIDTH: int = 6
_NAME_COLUMN_WIDTH: int = 16


class ExcelWorkbook:
    def __init__(self) -> None:
        self.wb: Workbook = Workbook()

    def write(self, filename: str) -> None:
        # We don't need or want the default worksheet.  It's easier to just
        # delete it than renaming it.  Based off of user input, there may be
        # a condition where we don't create any worksheets and that causes
        # a exception when saving.  To prevent this we're only deleting the
        # default sheet if we have created others.
        if len(self.wb.worksheets) > 1:
            self.wb.remove(self.wb["Sheet"])

        # Save the file
        self.wb.save(filename)

        # TODO: Needs try catch

    def _get_line(self, womens: str, mens: str) -> str:
        """Combines women/mens events and heats in three column mode.
        If there is a single gender, a seperator is not needed"""

        seperator: str = "/"

        if womens == "" or mens == "":
            seperator = ""

        return womens + seperator + mens

    def _create_unique_sheet(self, name: str) -> Worksheet:
        """Sheets are typicalled named based off of the session number.  To prevent
        duplicating names during testing, this function creates a unique tab name based
        on the initial 'name' passed in

            Args:
                name: Initial tab name

            Return:
                Correctly named worksheet in the workbook
        """
        sheet_name: str = name
        counter: int = 1

        while sheet_name in self.wb.sheetnames:
            sheet_name = f"{name}.{counter}"
            counter += 1

        return self.wb.create_sheet(sheet_name)

    def make_cheat_sheets(
        self, sessions: list[Session], three_column: bool = False
    ) -> None:
        """Takes a list of sessions and returns an MS Excel worksboot with a single tab per session.

        Args:
            sessions: List of sessions to be added to the XLS.  If tagged "merged," the sessions will
                      not be added to the XLS.
            three_column: Boolean flag whether a three (True) or Five (False) column sheet should be built
        """

        max_column: int = 3 if three_column else 5

        # do not process the original sessions that have been merged
        filtered_sessions = (s for s in sessions if not s.has_been_merged)

        for s in filtered_sessions:
            row_count = 1

            ws = self._create_unique_sheet(f"S{s.number}")
            if three_column:
                ws.column_dimensions[get_column_letter(1)].width = (
                    _EVENT_COLUMN_WIDTH * 2
                )
                ws.column_dimensions[get_column_letter(2)].width = _NAME_COLUMN_WIDTH
                ws.column_dimensions[get_column_letter(2)].width = (
                    _EVENT_COLUMN_WIDTH * 2
                )
            else:
                ws.column_dimensions[get_column_letter(1)].width = _EVENT_COLUMN_WIDTH
                ws.column_dimensions[get_column_letter(2)].width = _EVENT_COLUMN_WIDTH
                ws.column_dimensions[get_column_letter(3)].width = _NAME_COLUMN_WIDTH
                ws.column_dimensions[get_column_letter(4)].width = _EVENT_COLUMN_WIDTH
                ws.column_dimensions[get_column_letter(5)].width = _EVENT_COLUMN_WIDTH

            # header
            if three_column:
                ws.cell(row=1, column=1, value="W/M")
                ws.cell(row=1, column=2, value=f"Session {s.number}")
                ws.cell(row=1, column=3, value="W/M")
            else:
                ws.cell(row=1, column=1, value="W")
                ws.cell(row=1, column=2, value="H")
                ws.cell(row=1, column=3, value=f"Session {s.number}")
                ws.cell(row=1, column=4, value="M")
                ws.cell(row=1, column=5, value="H")

            cs: CheatSheet = CheatSheet(s)

            # all sessions
            for index, line in enumerate(cs.lines, start=2):
                row_count += 1

                # notes are on merged lines
                if line.is_note:
                    ws.merge_cells(
                        start_row=index,
                        start_column=1,
                        end_row=index,
                        end_column=max_column,
                    )
                    ws.cell(row=index, column=1, value=line.event_name)

                else:
                    if three_column:
                        ws.cell(
                            row=index,
                            column=1,
                            value=self._get_line(
                                str(line.womems_ev_num), str(line.mens_event_num)
                            ),
                        )
                        ws.cell(row=index, column=2, value=line.event_name)
                        ws.cell(
                            row=index,
                            column=3,
                            value=self._get_line(
                                str(line.womens_heat_count), str(line.mens_heat_count)
                            ),
                        )

                    else:
                        ws.cell(row=index, column=1, value=line.womems_ev_num)
                        ws.cell(row=index, column=2, value=line.womens_heat_count)
                        ws.cell(row=index, column=3, value=line.event_name)
                        ws.cell(row=index, column=4, value=line.mens_event_num)
                        ws.cell(row=index, column=5, value=line.mens_heat_count)

                # add border
                for c in range(1, (max_column + 1)):
                    # header row
                    ws.cell(row=1, column=c).font = _FONT_STYLE_BOLD
                    ws.cell(row=1, column=c).alignment = Alignment(
                        horizontal="center", vertical="center"
                    )

                    # event and note rows
                    for r in range(2, row_count + 1):
                        ws.cell(row=r, column=c).border = _THIN_BORDER
                        ws.cell(row=r, column=c).alignment = Alignment(
                            horizontal="center", vertical="center"
                        )

                        ws.cell(row=r, column=c).font = _FONT_STYLE

                # add border around the whole thing

    def make_event_durations(self, sessions: list[Session]):

        unmerged_sessions = (s for s in sessions if not s.merged_session)

        ws = self._create_unique_sheet("Duration")

        # 'row' always points to the first row to be written to
        row: int = 1
        for s in unmerged_sessions:
            ws.cell(row=row, column=1, value=f"\nSession {s.number}")
            ws.cell(row=row, column=1).font = Font(size="14", bold=True)
            row += 1

            row_offset: int = row

            for i in range(len(s.events)):
                start_time = s.events[i].datetime_start

                # use session end for the final event stop time
                if i == len(s.events) - 1:
                    finish_time: datetime = s.datetime_finish
                else:
                    finish_time = s.events[i + 1].datetime_start

                event_duration: timedelta = finish_time - start_time
                delta_in_minutes: int = round(event_duration.total_seconds() / 60)

                line1: str = f"{delta_in_minutes}-min "
                line2: str = f"h={s.events[i].heat_count}"
                line3: str = (
                    f"E{s.events[i].number} "
                    + f"{CheatSheet.short_gender(s.events[i].gender)} "
                    + f"{s.events[i].distance} "
                    + f"{CheatSheet.short_event(s.events[i].stroke)}"
                    + f"{' Relay' if s.events[i].is_relay else ''}"
                )

                ws.cell(row=row_offset + i, column=1, value=line1)
                ws.cell(row=row_offset + i, column=2, value=line2)
                ws.cell(row=row_offset + i, column=3, value=line3)
                row += 1

            # add a single row space before each column
            row += 1

    def _get_hours_mins(
        self, start_time: datetime, end_time: datetime
    ) -> tuple[int, int]:

        time_delta: timedelta = end_time - start_time
        delta_seconds: int = int(time_delta.total_seconds())
        minutes: int = delta_seconds // 60
        hours: int = minutes // 60

        # works whether hours >= 0
        remainder_minutes: int = minutes - (hours * 60)

        return (hours, remainder_minutes)


"""
   def make_session_diagnostics(self, sessions: list[Session]):

        unmerged_sessions = (s for s in sessions if not s.merged_session)

        ws = self._create_unique_sheet("Diagnostics")

        fontStyleHeader = Font(bold=True)

        redFill = PatternFill(
            start_color="FF0000", end_color="FF0000", fill_type="solid"
        )

        header_names: list[str] = [
            "Session",
            "Lanes",
            "Heats",
            "Splashes",
            "Interval",
            "+ Back",
            "Time",
            "12U Finish",
            "12U End Event",
        ]
        header_widths: list[int] = [10, 10, 10, 10, 10, 10, 10, 10, 20]

        # the two arrays above should stay the same length
        assert len(header_names) == len(header_names)

        # header
        for j in range(len(headerName)):
            ws.cell(1, j + 1, value=headerName[j])
            ws.column_dimensions[get_column_letter(j + 1)].width = headerWidth[j]
            ws.cell(1, j + 1).font = fontStyleHeader
            ws.cell(1, j + 1).alignment = Alignment(vertical="center")

        # write all session data
        for row, s in enumerate(unmerged_sessions, start=2):
            heats = 0
            splashes = 0

            # count all session heats and entries (aka 'splashes')
            for e in s.event:
                heats += e.heatCount
                splashes += e.totalEntries

            (hours, minutes) = self._get_hours_mins(s.datetimeStart, s.datetimeFinish)

            ws.cell(row, 1, value=f"{s.number}")
            ws.cell(row, 2, value=f"{s.poolSize}")
            ws.cell(row, 3, value=f"{heats}")
            ws.cell(row, 4, value=f"{splashes}")
            ws.cell(row, 5, value=f"{s.interval}")
            ws.cell(row, 6, value=f"{s.plusBackInterval}")

            ws.cell(row, 7, value=f"{hours}h {minutes}m")

            if s.last12Uevent is not None:
                final12U: int = s.event.index(s.last12Uevent)
                endTime12U: datetime

                # is it the final event in the session
                # if so, the final 12U is the session end time
                # len()-1 == last index
                if final12U == len(s.event) - 1:
                    endTime12U = s.datetimeFinish
                else:
                    # else, the final time is the start time of the
                    # event following the final 12U event
                    final12U += 1
                    endTime12U = s.event[final12U].datetimeStart

                (hours, minutes) = getHoursMins(s.datetimeStart, endTime12U)

                ws.cell(row, 8, value=f"{hours}h {minutes}m")
                ws.cell(
                    row,
                    9,
                    value=f"E{s.event[final12U].number} "
                    f"{s.event[final12U].distance} "
                    f"{shortEvent(s.event[final12U].name)}",
                )

                # if the 12U finish time is greater than 4-hours
                if hours >= 4:
                    cellToColor = ws.cell(row, 8)
                    cellToColor.fill = redFill

                    # count 12U heats
                    heats12U: int = 0
                    for i in range(final12U + 1):
                        heats12U += s.event[i].heatCount

                    savedMin: int = (heats12U * 5) // 60
                    line: str = f"12U Heats {heats12U}, 5-sec saves {savedMin}-min"
                    ws.cell(row, 10, value=line)
"""

if __name__ == "__main__":
    m: Meet = Meet(r".\tests\timeline_001.pdf")

    wb: ExcelWorkbook = ExcelWorkbook()

    wb.make_cheat_sheets(m.sessions)
    wb.make_cheat_sheets(m.sessions, True)
    wb.make_event_durations(m.sessions)

    wb.write("out.xlsx")

    # TODO
    # 1) Other sheets
    # A)   Event timeline  -- done,
    # B)   Four Hour check -- his can be added
    # C)   Seeding
    # 2) everything after merging
