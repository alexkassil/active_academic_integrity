from gspread_formatting import *
import gspread
from gspread.utils import rowcol_to_a1
import time
from config import master_sh, ASSIGNMENTS, num_students
# time.sleep(1)'s to conform with google sheets 100 requests/second in 100 seconds rule

sh = master_sh
worksheets = sh.worksheets()
master = sh.worksheet("Master")

columns = [[" sus", " accuse", " enforce"]]
column_num = 4

# email1 = ["lab01", "lab02", "hw01", "hw02"]
# email2 = ["lab03", "hw03", "proj01", "hw04", "lab05"]
# email3 = ["lab09","lab10", "lab11", "hw05", "hw06", "hw07", "proj02", "proj03"]

for worksheet in worksheets:
    title = worksheet.title
    if title in ASSIGNMENTS:
        master.update(
            rowcol_to_a1(1, column_num) + ":" + rowcol_to_a1(1, column_num + len(columns[0])),
            [[title + c for c in columns[0]]]
            )
        # Sus
        master.update(
            rowcol_to_a1(2, column_num) + ":" + rowcol_to_a1(num_students, column_num),
            [[str("=IF(AND(NE(IFERROR(vlookup($A%d, '%s'!A$2:E$" + str(num_students) + ", 2, FALSE), ),TRUE), IFERROR(vlookup($A%d, '%s'!A$2:E$" + str(num_students) + ", 3, FALSE), )=\"YES\"), \"YES\", )") % (i, title, i, title)] for i in range(2, num_students+1)],
            raw=False
        )
        print(title + " sus")
        # Accuse
        master.update(
            rowcol_to_a1(2, column_num+1) + ":" + rowcol_to_a1(num_students, column_num+1),
            [[str("=IF(IFERROR(vlookup($A%d, '%s'!A$2:E$" + str(num_students) + ", 4, FALSE))=TRUE, TRUE, )") % (i, title)] for i in range(2, num_students+1)],
            raw=False
        )
        print(title + " accuse")

        # Enforce
        # if title in email1:
        #     email1_offset = email1.index(title)
        #     ranges = rowcol_to_a1(2, column_num+2) + ":" + rowcol_to_a1(1000, column_num+2)
        #     master.update(
        #         ranges,
        #         [["=IFERROR(vlookup($A%d, email1!M$2:U$1000, %d, FALSE))" % (i, email1_offset+6)] for i in range(2, 1001)],
        #         raw=False
        #     )
        #     print(title + " enforce")
        # if title in email2:
        #     email2_offset = email2.index(title)
        #     ranges = rowcol_to_a1(2, column_num+2) + ":" + rowcol_to_a1(1000, column_num+2)
        #     master.update(
        #         ranges,
        #         [["=IFERROR(vlookup($A%d, email2!O$2:Y$1000, %d, FALSE))" % (i, email2_offset+7)] for i in range(2, 1001)],
        #         raw=False
        #     )
        #     print(title + " enforce")
        # if title in email3:
        #     email3_offset = email3.index(title)
        #     ranges = rowcol_to_a1(2, column_num+2) + ":" + rowcol_to_a1(1000, column_num+2)
        #     master.update(
        #         ranges,
        #         [["=IFERROR(vlookup($A%d, email3!S$2:AI$1000, %d, FALSE))" % (i, email3_offset+10)] for i in range(2, 1001)],
        #         raw=False
        #     )
        #     print(title + " enforce")
        column_num += 3
        time.sleep(1)

# Email Sent waves!
# wave_formula = [
#     "=IFERROR(vlookup($A%d, email1!Z$2:AA$100, 2, FALSE))",
#     "=IFERROR(vlookup($A%d, email2!AE$2:AF$100, 2, FALSE))",
#     "=IFERROR(vlookup($A%d, email3!AR$2:AS$200, 2, FALSE))",
#     ]
# for i in range(1, len(wave_formula)+1):
#     master.update(
#         rowcol_to_a1(1, column_num),
#         [["Email Sent Wave " + str(i)]]
#     )
#     master.update(
#         rowcol_to_a1(2, column_num) + ":" + rowcol_to_a1(1000, column_num),
#         [[wave_formula[i-1] % (j,)] for j in range(2, 1001)],
#         raw=False
#     )
    
#     column_num +=1
#     print("Email wave " + str(i))
#     time.sleep(1)
