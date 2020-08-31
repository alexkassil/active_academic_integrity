"""
Applies academic integrity penalties. Usage:

python ai_enforce_penalties.py FILE

given a file with the format

```
student1@berkeley.edu lab03 hw05 
student2@berkeley.edu hw01 lab04
```

which is space delimited, with commas being meaningless.
"""
import click
import requests
import tqdm
import subprocess
import json
API_BASE = "https://ok.cs61a.org/api/v3"

submission_ids = {}
assignments = {}

def update_submission_ids(course, assignment, token):
    api_url = API_BASE + "/assignment/{0}/{1}/submissions?limit=1000&access_token={2}"
    endpoint = api_url.format(course, assignment, token)
    try:
        r = requests.get(endpoint, timeout=60)
        data = r.json()
        backups = data['data']['backups']
        with open('test_submissions.txt', 'w') as outfile:
        	json.dump(backups, outfile)
        for b in backups:
        	if b['submitter']['email'] in assignments[assignment]:
        		submission_ids[b['id']] = [assignment, b['submitter']['email']]
    except Exception as e:
        click.echo("Error fetching {} - {}".format(endpoint, e), err=True)

def apply_penalty(bid, token):
    data = {
    'bid': bid, 
    'score': 0.0, 
    'kind': 'Total',
    'message': 'Academic Integrity Penalty'}
    url = 'https://okpy.org/api/v3/score/?access_token={}'
    r = requests.post(url.format(token), data=data)
    response = r.json()


def get_token():
    return subprocess.call(['python3', 'ok', '--get-token'])

def is_assignment(token):
    if token.startswith("lab") or token.startswith("hw"):
        return True
    elif token in {"hog", "cats", "ants", "scheme"}:
        return True
    return False

def process(line):
    email, parsed = parse_line(line)

    for assign in parsed:
    	if assign[0] in assignments:
    		assignments[assign[0]] += [email]
    	else:
    		assignments[assign[0]] = [email]

def parse_line(inp):
    items = inp.lower().replace(",", " ").split()
    email = items.pop(0)
    assert "@" in email
    result = []
    while items:
        token = items.pop(0)
        if is_assignment(token):
            result.append([token])
            continue
        name = items.pop(0)
        result[-1].append((token, name))
    return email, result

@click.command()
@click.option('--token', prompt="Ok Token (python3 ok --get-token) or copy from above")
@click.option('--course', prompt='Course ID on OK (example: cal/cs61a/su20)')
@click.option('--file', prompt='File containing emails and assignments (example: penalties.txt)')
@click.option('--lgtm/--skip-lgtm', default=True)
def main(token, course, file, lgtm):
    # Remove leading/trailing whitespace
    token = token.strip()
    with open(file) as f:
        for line in f:
            process(line)
    print("assignments:", assignments)
    for assign in assignments.keys():
        update_submission_ids(course, assign, token)
    print("submission ids:", submission_ids)
    for bid in submission_ids.keys():
    	if lgtm:
    		print("bid:", bid)
    		print("assignment:", submission_ids[bid][0])
    		print("email:", submission_ids[bid][1])
    	if not lgtm or input("lgtm^ [y/n]: ").strip() == "y":
    		apply_penalty(bid, token)


if __name__ == '__main__':
    get_token()
    main()
