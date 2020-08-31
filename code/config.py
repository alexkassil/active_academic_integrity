"""

File which contains all the defaults to set

"""
import gspread

ASSIGNMENTS = ['lab%.2d'  % x for x in range(15  )] + \
              ['hw%.2d'   % x for x in range(1, 10)] + \
              ['proj%.2d' % x for x in range(1, 5)]

# commandline python command
python = "python3"

# Roster file 
# usually from okpy, but any csv of below format will do, leave empty what isn't present
# email,name,sid,class_account,section,role
roster_file = "roster.csv"

API_BASE = "https://okpy.org/api/v3"


master_spreadsheet_direct_link = "https://docs.google.com/spreadsheets/"

gc = gspread.service_account()
master_sh = gc.open_by_url(master_spreadsheet_direct_link)

# num students upperbound
num_students = 2200
