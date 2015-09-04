#!/usr/bin/python
# Author: "Eduard Trott" <etrott@redhat.com>

# SHORT SUMMARY:
# - gspread do not allow creation of new sreadsheets
# - gdata allow it, but do not support authorization with credentials and have terrible documentation
# - apiclient allow both, but gspread more comfortable for spreadsheet editing


from distutils.util import strtobool
import httplib2
import os
import re
import sys
from string import ascii_uppercase


from apiclient import discovery
import gspread
import oauth2client
import pandas as pd

from utils import CLIENT_SECRET_FILE, logr

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[oauth2client.tools.argparser]).parse_args()
except ImportError:
    flags = None

# FIXME: clarify scopes
SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
            'https://www.googleapis.com/auth/drive '
            'https://spreadsheets.google.com/feeds '
            'https://docs.google.com/feeds')

def get_credentials():
    """
    FIXME DOCs
    Taken from:
    https://developers.google.com/drive/web/quickstart/python
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:

        flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        if flags:
            credentials = oauth2client.tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = oauth2client.tools.run(flow, store)
        logr.info('Storing credentials to ' + credential_path)
    return credentials


def export(df, path="/New Spreadsheet", wks_name="Sheet1"):
    '''
    FIXME DOCs
    '''
    # access credentials
    credentials = get_credentials()
    # auth for apiclient
    http = credentials.authorize(httplib2.Http())
    # auth for gspread
    gc = gspread.authorize(credentials)
    # FIXME: Different versions have different keys like v1:id, v2:fileId
    service = discovery.build('drive', 'v2', http=http)

    about = service.about().get().execute()

    file_id = about['rootFolderId']
    
    path = path.split('/')

    # folder/folder/folder/spreadsheet
    f_types = ['folder']*(len(path)-1)+['spreadsheet']
    f_types = ['application/vnd.google-apps.'+ f for f in f_types]
    for name, f_type in zip(path, f_types):
        if name == '':
            continue
        file_exists = False
        # searching for all files in gdrive with given name
        files = service.files().list(q="title = '%s'" %(name,)).execute()['items']
        for f in files:
            # if file not trashed and previos file(or root for first 
            # file) in parents then remember file id
            if not f['labels']['trashed'] and \
                    any([file_id in parent['id'] for parent in f['parents']]):
                file_id = f['id']
                file_exists = True
                break
        #  else create a new file
        if not file_exists:
            body = {
                'mimeType': f_type,
                'title': name,
                'parents': [{"id": file_id}]
            }
            file_id = service.files().insert(body=body).execute(http=http)['id']

    # connection to created spreadsheet via gspread
    tmp_wks = None
    try:
        spsh = gc.open_by_key(file_id)
        wkss = spsh.worksheets()
        if any(map(lambda wks: re.match(r"<Worksheet '%s' id:\S+>"%(wks_name),
                                                         str(wks)), wkss)):
            # http://stackoverflow.com/a/27293138/1289080
            try:
                input = raw_input
            except NameError:  # Python 3
                pass

            respond = input("'%s' worksheet already exists. '"
                                "Do you want to rewrite it?(y/n) "%(wks_name))
            if not strtobool(respond):
                sys.exit(1)
            if len(wkss)==1:
                tmp_wks = spsh.add_worksheet('tmp', 1, 1)
            wks = spsh.worksheet(wks_name)
            spsh.del_worksheet(wks)

        wks = spsh.add_worksheet(wks_name, 1000, 100)
        if tmp_wks:
            spsh.del_worksheet(tmp_wks)

    except gspread.httpsession.HTTPError as e:
        logr.error('Status:', e.response.status)
        logr.error('Reason:', e.response.reason)
        raise

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    last_idx = len(df.index)

    seq_num = len(df.columns)
    last_col = ''
    while seq_num >= 0:
        last_col = ascii_uppercase[seq_num%len(ascii_uppercase)]+last_col
        seq_num = seq_num // len(ascii_uppercase) - 1

    # if pandas dataframe large then given worksheet then increes num of cols or rows
    if len(df.index)+1 > wks.row_count:
        wks.add_rows(len(df.index)-wks.row_count+1)

    if len(df.columns)+1 > wks.col_count:
        wks.add_cols(len(df.columns)-wks.col_count+1)

    # FIXME: NaN value in gspreadsheets

    # Addition of col names
    cell_list = wks.range('B1:%s1'%(last_col, ))
    for idx, cell in enumerate(cell_list):
        cell.value = df.columns.values[idx]
    wks.update_cells(cell_list)

    # Addition of row names
    cell_list = wks.range('A2:A%d'%(last_idx+1, ))
    for idx, cell in enumerate(cell_list):
        cell.value = df.index[idx]
    wks.update_cells(cell_list)

    # Addition of cell values
    cell_list = wks.range('B2:%s%d'%(last_col, last_idx+1))
    for j, idx in enumerate(df.index):
        for i, col in enumerate(df.columns.values):
            cell_list[i+j*len(df.columns.values)].value = df[col][idx]
    wks.update_cells(cell_list)