from xlwt import Workbook, easyxf
from datetime import date


class ExcelReport:
    """Designed to help with generating excel reports. Use write_header(),
    followed by write_section() and write_entry() for each section and their
    entries"""

    def __init__(self, num_cols):
        """num_cols is required to properly format the sheet"""
        self.w = Workbook()
        self.ws = self.w.add_sheet('Report')
        self.row = 0
        self.cols = num_cols - 1
        for i in range(0, self.cols + 1):
            self.ws.col(i).width = 5000

    def write_header(self, title):
        """Write the name of the report and date at the top"""
        title_style = easyxf('font: name Arial, height 400;')
        date_style = easyxf(
            'font: name Arial, height 240; alignment: horizontal left;',
            num_format_str='YYYY-MM-DD'
        )

        self.ws.write(self.row, 0, title, title_style)
        self.row += 2

        self.ws.write(self.row, 0, date.today(), date_style)

    def write_section_head(self, text, columns):
        """Draw a section head and subhead to precede entries. Text will be
        inserted within the heading, while columns should be a list of strings
        representing column names"""
        # Add space above section
        self.row += 2

        # Define section head styles
        background = 'pattern: pattern solid, fore_colour gray_ega;'
        top_left = easyxf('border: left thin, top thin;' + background)
        top = easyxf('border: top thin;' + background)
        top_right = easyxf('border: right thin, top thin;' + background)
        right = easyxf('border: right thin;' + background)
        bottom_right = easyxf('border: right thin, bottom thin;' + background)
        bottom = easyxf('border: bottom thin;' + background)
        bottom_left = easyxf('border: left thin, bottom thin;' + background)
        left = easyxf('font: bold True; border: left thin;' + background)
        middle = easyxf(background)

        # Define sub head styles
        subhead_bg = 'pattern: pattern solid, fore_colour gray25;'
        subhead_left = easyxf('border: left thin, top thin, bottom thin;' + subhead_bg)
        subhead_middle = easyxf('border: top thin, bottom thin;' + subhead_bg)
        subhead_right = easyxf('border: right thin, top thin, bottom thin;' + subhead_bg)

        # Draw the section head borders and bg
        self.ws.write(self.row, 0, style=top_left)
        self.ws.write(self.row, self.cols, style=top_right)

        self.ws.write(self.row + 1, 0, text, style=left)
        self.ws.write(self.row + 1, self.cols, style=right)

        for i in range(1, self.cols):
            self.ws.write(self.row, i, style=top)
            self.ws.write(self.row + 1, i, style=middle)
            self.ws.write(self.row + 2, i, style=bottom)

        self.ws.write(self.row + 2, 0, style=bottom_left)
        self.ws.write(self.row + 2, self.cols, style=bottom_right)

        self.row += 3

        # Draw the sub head
        i = 0
        for column in columns:
            if i == 0:
                self.ws.write(self.row, i, column, subhead_left)
            elif i == len(columns) - 1:
                self.ws.write(self.row, i, column, subhead_right)
            else:
                self.ws.write(self.row, i, column, subhead_middle)
            i += 1

        self.row += 1

    def write_entry(self, entry):
        """Given an array, entry, it populates a single row"""
        format = "%d %b %Y %I:%M%p"

        for i in range(0, len(entry)):
            # Format dates, remove timezone info
            if hasattr(entry[i], 'hour'):
                entry[i] = entry[i].strftime(format)
            self.ws.write(self.row, i, entry[i])

        self.row += 1

    def save(self, path):
        self.w.save(path)
