import os
import click
from tqdm import tqdm
from gspread_formatting import *
import gspread
import pickle
from config import master_sh, num_students

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
filetypes = {".py", ".scm", ".sql"}
ASSIGNMENTS = ['lab%.2d'  % x for x in range(15  )] + \
              ['hw%.2d'   % x for x in range(1, 10)] + \
              ['proj%.2d' % x for x in range(1, 5)]

suspicious_rule = DataValidationRule(
    BooleanCondition('ONE_OF_LIST', ['yes', 'no']),
    showCustomUi=True
)

second_look_rule = DataValidationRule(
    BooleanCondition('BOOLEAN', ['TRUE', 'FALSE'])
)

def get_or_create_new(sh, worksheet_title, cols="26"):
    """
    Either get the worksheet by title, or make a new one
    """
    for worksheet in sh.worksheets():
        if worksheet.title == worksheet_title:
            return worksheet
    return sh.add_worksheet(title=worksheet_title, rows=str(num_students), cols=cols)


def uncollated_merge(lst1, lst2):
    return [lst2[i//2] if i % 2 else lst1[i//2] for i in range(len(lst1)*2)]

# Search a specific directory for search terms
def student_search_py(student_dir, search_terms):
    found = ["" for _ in search_terms]
    for filename in os.listdir(student_dir):
        f_okpy, f_data = "", ""
        with open(student_dir + "/" + filename, "r", encoding="utf-8") as f:
            f_okpy = f.readline()
            f_data = f.read()
        for i in range(len(search_terms)):
            if not found[i] and search_terms[i] in f_data:
                found[i] = f_okpy[1:-1]
        if all(found):
            return found
    return found

# Search files for all search terms
def search_all_py(searches):
    flagged = {}
    for search_dir in searches:
        flagged[search_dir] = []
        print("Searching {} for {}".format(search_dir, searches[search_dir]))
        for student in tqdm(os.listdir(search_dir)):
            result = student_search_py(search_dir + "/" + student, searches[search_dir])
            if any(result):
                flagged[search_dir].append([student] + result)
    return flagged

# Find what filtered functions are available for an assignment
def get_availability(assignment):
    available_to_search = {}
    for f in os.listdir("."):
        if f.find(assignment) == 0 and any([ext in f for ext in filetypes]):
            f = f[f.find("_")+1:]
            if f.find("_") == -1:
                if f not in available_to_search:
                    available_to_search[f] = []
                available_to_search[f].append(f)
            else:
                filename, function = f[:f.find("_")], f[f.find("_")+1:]
                if filename not in available_to_search:
                    available_to_search[filename] = []
                available_to_search[filename].append(function)
    return available_to_search

# Get search terms from user
def get_searches_input(assignment, available_to_search):
    searches = {}
    for file in available_to_search:
        for function in available_to_search[file]:
            directory = assignment + "_" + file
            prompt = "Enter phrase to search in {}:ENTIRE_FILE (blank to move on): ".format(file)
            if function != file:
                directory += "_" + function
                prompt = "Enter phrase to search in {}:{} (blank to move on): ".format(file, function)
            phrase = input(prompt)
            while phrase.strip() != "":
                if directory not in searches:
                    searches[directory] = []
                searches[directory].append(phrase)
                phrase = input(prompt)
    return searches

# From upload_to_spreadsheet.py
def upload_sheet(sh, title, header, cells, verify=True):
    if verify:
        print("Title of tab will be " + title)
        print(header)
        print(cells[:1])
        command = input("Do the first rows shown above look correct? y/n: ")
        if command != "y":
            print("Aborting -- received input " + command)
            exit()
    else:
        print("\t" + title)
    worksheet = get_or_create_new(sh, title, cols=len(header[0]))
    worksheet.update("A1:" + gspread.utils.rowcol_to_a1(1, len(header[0])), header)
    worksheet.freeze(rows=1)

    for i in range(len(header[0])):
        th = header[0][i]
        col = alphabet[i]
        entire_col = col + '2:' + col + str(num_students)
        if "sus?" in th:
            set_data_validation_for_cell_range(worksheet, entire_col, suspicious_rule)
        if "second look" in th:
            set_data_validation_for_cell_range(worksheet, entire_col, second_look_rule)
        if "numSuspicious" in th:
            count = "COUNTIF(B{}:" + alphabet[i-1] + "{},\"yes\")"
            worksheet.update(entire_col, [["=IF(" + count.format(j, j) + ">0," + count.format(j, j) + ",\"\")"] for j in range(2, len(cells)+2)], value_input_option='USER_ENTERED')

    bottom_left_corner = gspread.utils.rowcol_to_a1(len(cells)+1, len(cells[0]))
    worksheet.update("A2:" + bottom_left_corner, cells)
def upload_to_spreadsheet(assignment, name, searches, results, count_sus):
    sh = master_sh
    print("Writing to " + sh.url)
    for search_dir in results:
        search_terms = searches[search_dir]
        cells = results[search_dir]
        extra_cols = ["second look", "comments"]
        if count_sus:
            extra_cols = ["numSuspicious"] + extra_cols
        header = [["email"] + uncollated_merge(search_terms, ["sus?" for _ in search_terms]) + extra_cols]
        for row in cells:
            row[1:] = uncollated_merge(row[1:], ["" for _ in row[1:]])
        upload_sheet(sh, assignment, header, cells)

@click.command()
@click.option('--assignment', prompt="Course assignment (example: lab00)")
@click.option('--name', prompt="Uploader name (example: Alex)")
@click.option('--search/--no-search', default=True)
@click.option('--upload/--no-upload', default=True)
@click.option('--count-sus/--no-count-sus', default=False)

def main(assignment, name, search, upload, count_sus):
    assert assignment in ASSIGNMENTS, "error %s not in %s" % (assignment, str(ASSIGNMENTS))
    # (5) SEARCH FOR TEXT
    # Output: "{assignment}_search_results.pickle"
    if search:
        available_to_search = get_availability(assignment)
        searches = get_searches_input(assignment, available_to_search)
        results = search_all_py(searches)
        for search_dir in results:
            print("{} summary".format(search_dir))
            for i in range(len(searches[search_dir])):
                search_term = searches[search_dir][i]
                print("\t\"{}\": {} hits".format(search_term, sum([1 for row in results[search_dir] if row[i+1]])))
        with open(assignment + "_search_results.pickle", "wb") as f:
            pickle.dump((searches, results), f)
    else:
        with open(assignment + "_search_results.pickle", "rb") as f:
            searches, results = pickle.load(f)
    # (6) UPLOAD TO SPREADSHEET
    if upload:
        upload_to_spreadsheet(assignment + " okpy", name, searches, results, count_sus=count_sus)
    else:
        print(results)

if __name__ == '__main__':
    main()
