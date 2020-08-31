import csv
import json
import hashlib
import os
import shutil
import subprocess
import click
import requests
import gspread
import argparse
import sys
import dateutil.parser

from tqdm import tqdm
from config import ASSIGNMENTS, API_BASE, python, master_sh

def get_token():
    return subprocess.call([python, 'ok', '--get-token'])
def hash_email(email):
    return hashlib.md5(email.encode()).hexdigest()
def get_submission(endpoint, fname, student_hash):
    try:
        r = requests.get(endpoint, timeout=60)
        data = r.json()
        backups = data['data']['backups']
        with open(fname, 'w', encoding="utf-8") as outfile:
            for b in backups:
                b['submitter_hash'] = student_hash
            json.dump(backups, outfile)
    except Exception as e:
        click.echo("Error fetching {} - {}".format(endpoint, e), err=True)
def get_assignment(token, course_assignment, emails, anon=False, disable_t=False):
    api_url = API_BASE + "/assignment/{0}/export/{1}?limit=1000&access_token={2}"
    folder = "./exports/{}".format(course_assignment.replace('/','-'))
    if not os.path.exists(folder):
        os.mkdir(folder)
    for student in tqdm(emails, disable=disable_t):
        endpoint = api_url.format(course_assignment, student, token)
        student_hash = hash_email(student) if anon else student
        fname = '{0}/{1}.json'.format(folder, student_hash)
        get_submission(endpoint, fname, student_hash)
def get_student(token, assignment, email):
    return get_assignment(token, assignment, [email], disable_t=False)

# From update_roster.py
def get_roster(assignment, roster_file):
    sh = master_sh
    assert assignment in ASSIGNMENTS, "Error, assignment should be one of " + str(ASSIGNMENTS)
    with open(roster_file, "r", encoding="utf-8") as roster:
        roster_data = csv.reader(roster)
        emails = [row[0] for row in roster_data if (row[0] != 'email' and '@' in row[0])]
    past_worksheet = sh.worksheet("Past Work").get_all_values()
    assignment_col_num = ASSIGNMENTS.index(assignment) + 14
    past_worksheet = [[past_worksheet[i][0], past_worksheet[i][assignment_col_num]] for i in range(len(past_worksheet))]
    with open(assignment + "_roster.csv", "w", encoding="utf-8") as output_roster:
        writer = csv.writer(output_roster)
        writer.writerow(["email"])
        past_work_emails = set([email for email, bool_str in past_worksheet if bool_str == "TRUE"])
        for email in emails:
            if email not in past_work_emails:
                writer.writerow([email])    
    return assignment + "_roster.csv"

# From parse_exports.py
def do_parse_exports(course, assignment, submitted_file, time_cutoff=None):
    input_directory = "exports/{}/".format((course + "/" + assignment).replace('/','-'))
    output_directory = assignment + "_" + submitted_file + "/"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    filenames = os.listdir(input_directory)
    for filename in tqdm(filenames):
        email = filename[:-5]
        count = 1
        if not os.path.exists(output_directory + email):
            os.mkdir(output_directory + email)
        with open(input_directory + filename, encoding="utf-8") as json_data:
            d = json.load(json_data)
            for entry in sorted(d, key=lambda x: dateutil.parser.isoparse(x['created'])):
                # Skip over entries before the time cutoff
                if time_cutoff is not None and dateutil.parser.isoparse(entry['created']) < time_cutoff:
                    continue
                for message in entry['messages']:
                    if message['kind'] == 'file_contents':
                        try:
                            with open(output_directory + email + '/' + str(count) + '_' + submitted_file, 'w', encoding="utf-8") as f:
                                print("#https://okpy.org/admin/grading/" + entry['id'], file=f)
                                print(message['contents'][submitted_file], file=f)
                                count += 1
                        except Exception as e:
                            print("Exception", e)
                            pass

@click.command()
@click.option('--token', prompt="Ok Token (python3 ok --get-token) or copy from above")
@click.option('--course', prompt='Course ID on OK (example: cal/cs61a/su20)')
@click.option('--assignment', prompt="Course assignment (example: lab00)")
@click.option('--file', prompt="Assignment filename, comma separated if multiple (example: lab00.py)")
@click.option('--roster', prompt="roster, downloaded from okpy")
@click.option('--generate-roster/--skip-generate-roster', default=False)
@click.option('--download-okpy/--skip-download-okpy', default=True)
@click.option('--parse-exports/--skip-parse-exports', default=True)

def main(token, course, assignment, roster, file, generate_roster, download_okpy, parse_exports):
    # (1) GENERATE ASSIGNMENT ROSTER
    # Opens "{roster_file}", outputs "{assignment}_roster.csv"
    if generate_roster:
        print("(1) Generating {} roster from Master Spreadsheet".format(assignment))
        roster = get_roster(assignment, roster)

    # (2) DOWNLOAD OKPY FILES
    # Creates "exports/{course}-{assignment}" directory, outputs .json files into said directory
    if download_okpy:
        print("(2) Downloading {} files from okpy".format(assignment))
        with open(roster, "r", encoding="utf-8") as roster_file:
            roster_data = csv.reader(roster_file)
            emails = [row[0] for row in roster_data if (row != [] and row[0] != 'email' and '@' in row[0])]
            get_assignment(token, course + "/" + assignment, emails)

    # (3) PARSE EXPORTS
    # Creates "{assignment}_{file}" directory for each file, outputs .py files into said directory
    if parse_exports:
        print("(3) Parsing exports for {}".format(assignment))
        for filename in file.split(","):
            print(filename.strip())
            do_parse_exports(course, assignment, filename.strip())

if __name__ == '__main__':
    if not os.path.exists("./exports"):
        os.mkdir("./exports")
    if "--token" not in sys.argv and "--skip-download-okpy" not in sys.argv:
        get_token()
    main()
