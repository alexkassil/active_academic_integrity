# active_academic_integrity


# Setup instructions
1. To allow python to interact with google sheets, install the requirements `pip3 install -r requirements.txt` follow [this guide](https://gspread.readthedocs.io/en/latest/oauth2.html#service-account) to set up a service account
  ex: service@servce.iam.gserviceaccount.com

2. Copy this [spreadsheet](https://docs.google.com/spreadsheets/d/1Q36Sem2cT2pcCmu1CwvjE_CbUcIZ2S_SV_o11X0Xj4c/edit?usp=sharing) and share it with the service account made in step 1 and update config.py with the correct spreadsheet url, list of assignment strings, and add roster file to code folder.

# Workflow
1. Make changes to the assignment before it is released to the class. Big distinct changes are best
  ex: recursive function call add_grades change to add_bananas
  ex: sql table change name
  ex: change string to be printed completely
  non ex: change f to h, or x to y, since students can be confused
  
2. Download backups from okpy by running `python3 ai_files.py`

3. (optional) Filter different functions by running `python3 ai_filter.py`. Useful when different functions might have false positives with terms searched

4. Find suspicious past semester keywords by running `python3 ai_find.py` and upload them. Now you can go to master spreadsheet and decide which backups are suspicious

5. Run `python3 manage_master_spreadsheet.py` after updating the assignemnt variable. Now you can sort decreasing by times flagged and decide who to accuse.

6. Run `python3 master_spreadsheet_master_tab.py` to aggregate info into master tab.
