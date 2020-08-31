import argparse
from gspread_formatting import *
import gspread
from gspread.utils import rowcol_to_a1
from config import ASSIGNMENTS, master_sh, gc, num_students

sh = master_sh
worksheets = sh.worksheets()
PAST_WORK_OFFSET = 14

assignment = 'lab00'
debug = True
column = 0

# Add the two new sheets to the master spreadsheet

def get_letter(num):
    return rowcol_to_a1(1, num)[:-1]

def get_or_create_new(worksheet_title):
    """
    Either get the worksheet by title, or make a new one
    """
    for worksheet in worksheets:
        if worksheet.title == worksheet_title:
            return worksheet
    return sh.add_worksheet(title=worksheet_title, rows=str(num_students), cols="26")

#gspread.utils.rowcol_to_a1(len(cells[0])+1, 2)
to_sheet = get_or_create_new(assignment)
from_sheet = get_or_create_new(assignment + ' okpy')

print(to_sheet, from_sheet)

"""# Populate okpy worksheet
okpy_sh = gc.open(assignment)
okpy_sh_wk = okpy_sh.get_worksheet(1)
top_row = okpy_sh_wk.row_values(1)
# remove email/second look/comments column, and then divide by 2
# ex: ['email', 'out of stock', 'sus?', 'generate_paths', 'sus?', 'second look', 'comments']
okpy_sh_cols = (len(top_row) - 3) // 2
# Add import to top left
from_sheet.update(
    "A1",
    [['=IMPORTRANGE("%s", "%s!A1:%s200")' % (okpy_sh.url, okpy_sh_wk.title, get_letter(len(top_row))) ]],
    raw=False
)
print(okpy_sh_wk)
"""
columns = [["email", "Past Work?", "Suspicous?", "Accuse?", "Times Flagged"]]

to_sheet.update(
    "A1:E1",
    columns
)
to_sheet.freeze(rows=1)
# Email
to_sheet.update(
    "A2:A"+str(num_students),
    [[str("=IFERROR(vlookup(Master!A%d, 'Updated Roster'!A$1:A$" + str(num_students) + ", 1, FALSE), )")%(i,)] for i in range(2, num_students + 1)],
    raw = False
)
# Past Work?
to_sheet.update(
    "B2:B" + str(num_students),
    [[str("=IFERROR(vlookup($A%d, 'Past Work'!A$2:AO$" + str(num_students) + ", %d, False), )")%(i,ASSIGNMENTS.index(assignment) + PAST_WORK_OFFSET)] for i in range(2, num_students + 1)],
    raw = False
)

# Times flagged
to_sheet.update(
    "E2:E" + str(num_students),
    [[str('=COUNTIF(F%d:Z%d, "=yes")') % (i, i)] for i in range(2, num_students + 1)],
    raw = False
    )
# Suspicious?
to_sheet.update(
    "C2:C" + str(num_students),
    [[str('=IF(E%d>0, "YES", "")') % (i)] for i in range(2, num_students + 1)],
    raw = False
    )
# Data Validation Accuse?
accuse_rule = DataValidationRule(
    BooleanCondition('BOOLEAN', ['TRUE', 'FALSE'])
)
set_data_validation_for_cell_range(to_sheet, 'D2:D' + str(num_students), accuse_rule)



# Gross python to get search term
def get_search_term(column=0, from_sheet=from_sheet):
    return from_sheet.get(rowcol_to_a1(1, (column + 1) * 2))[0][0]

column_nums = range((len(from_sheet.row_values(1)) - 3) // 2)
for column in column_nums:    
    start_column = len(columns[0]) + 1 + (column * 3)
    term = get_search_term(column)
    print("column: %d, term: %s" % (column, term))
    new_cols = [" links", " sus", " comments"]
    to_sheet.update(
        rowcol_to_a1(1, start_column) + ":" + rowcol_to_a1(1, start_column+3),
        [ [term + x for x in new_cols] ]
    )
    # % (row_num, okpy_file, start_column_letter, start_column_letter+3, col_number (2, 3, or 4))
    okpy_col = "=IFERROR(vlookup($A%d, '%s'!%s$2:%s$" + str(num_students) + ", %d, FALSE), \"\")"
    x = okpy_col % (2, 'lab01 okpy', 'A', 'D', 2)
    def make_col(okpy_name, column):
        total_length = len(from_sheet.row_values(1))
        start_col = "A"
        end_col = get_letter(total_length)
        return [[
            okpy_col % (i, okpy_name, start_col, end_col, 2 + column * 2),
            okpy_col % (i, okpy_name, start_col, end_col, 3 + column * 2),
            okpy_col % (i, okpy_name, start_col, end_col, total_length),
        ] for i in range(2, num_students+1)]

        start_col, end_col = get_letter(1 + column * 5) , get_letter(4 + column * 5)
        return [[
            okpy_col % (i, okpy_name, start_col, end_col, 2),
            okpy_col % (i, okpy_name, start_col, end_col, 3),
            okpy_col % (i, okpy_name, start_col, end_col, 4),
        ] for i in range(2, num_students+1)]

    cols = make_col(assignment + ' okpy', column)
    to_sheet.update(
        rowcol_to_a1(2, start_column) + ":" + rowcol_to_a1(num_students, start_column+3),
        cols, raw=False
    )
