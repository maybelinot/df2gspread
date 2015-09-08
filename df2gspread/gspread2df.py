#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-08 09:59:24
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2015-09-08 09:59:43

# SHORT SUMMARY of alternative google spreadsheet python modules:
# - gspread do not allow creation of new sreadsheets
# - gdata allow it, but do not support authorization with credentials
#   and have terrible documentation
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
import numpy as np

from utils import CLIENT_SECRET_FILE, logr, get_credentials


# FIXME: clarify scopes
SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
          'https://www.googleapis.com/auth/drive '
          'https://spreadsheets.google.com/feeds '
          'https://docs.google.com/feeds')


def export(path="/New Spreadsheet", wks_name="Sheet1", col_names=False,
           row_names=False):
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

    pathway = path.split('/')

    # folder/folder/folder/spreadsheet
    for name in pathway:
        if name == '':
            continue
        file_exists = False
        # searching for all files in gdrive with given name
        files = service.files().list(
            q="title = '%s'" % (name,)).execute()['items']
        for f in files:
            # if file not trashed and previos file(or root for first
            # file) in parents then remember file id
            if not f['labels']['trashed'] and \
                    any([file_id in parent['id'] for parent in f['parents']]):
                file_id = f['id']
                file_exists = True
                break
        #  else error
        if not file_exists:
            sys.exit("Spreadsheet '%s' is not exist" % (path))

    wsheet_match = lambda wks: re.match(
        r"<Worksheet '%s' id:\S+>" % (wks_name), str(wks))
    # connection to created spreadsheet via gspread
    tmp_wks = None
    try:
        spsh = gc.open_by_key(file_id)
        wkss = spsh.worksheets()
        if any(map(wsheet_match, wkss)):
            wks = spsh.worksheet(wks_name)
        else:
            sys.exit("Worksheet '%s' is not exist" % (wks_name))
    except gspread.httpsession.HTTPError as e:
        logr.error('Status:', e.response.status)
        logr.error('Reason:', e.response.reason)
        raise

    raw_data = wks.get_all_values()

    if not raw_data:
        sys.exit()

    if row_names and col_names:
        row_names = [row[0] for row in raw_data[1:]]
        col_names = raw_data[0][1:]
        raw_data = [row[1:] for row in raw_data[1:]]
    elif row_names:
        row_names = [row[0] for row in raw_data]
        col_names = np.arange(len(raw_data[0]) - 1)
        raw_data = [row[1:] for row in raw_data]
    elif col_names:
        row_names = np.arange(len(raw_data) - 1)
        col_names = raw_data[0]
        raw_data = raw_data[1:]
    else:
        row_names = np.arange(len(raw_data))
        print(row_names)
        col_names = np.arange(len(raw_data[0]))
        print(col_names)

    df = pd.DataFrame([pd.Series(row) for row in raw_data], index=row_names)
    df.columns = col_names

    return df


if __name__ == "__main__":
    # Basic test
    import gspread2df

    path = '/some/Platform QE All-Hands Event Survey (Responses)'
    wks_name = 'Form Responses 1'

    df = gspread2df.export(path, wks_name, col_names=True)
    print(df)
