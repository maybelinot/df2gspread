#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:54:47
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-19 14:01:20

import re
import httplib2

from apiclient import discovery, errors
import gspread

from .utils import logr


def get_file_id(credentials, gfile, write_access=False):
    """DOCS..."""
    # auth for apiclient
    http = credentials.authorize(httplib2.Http())
    # FIXME: Different versions have different keys like v1:id, v2:fileId
    service = discovery.build('drive', 'v2', http=http)
    about = service.about().get().execute()

    file_id = about['rootFolderId']
    pathway = gfile.split('/')

    if write_access:
        f_types = ['folder'] * (len(pathway) - 1) + ['spreadsheet']
        f_types = ['application/vnd.google-apps.' + f for f in f_types]

    # folder/folder/folder/spreadsheet
    for idx, name in enumerate(pathway):
        if name == '':
            continue
        file_exists = False
        # searching for all files in gdrive with given name
        files = service.files().list(
            q="title = '%s'" % (name,)).execute()['items']
        for f in files:
            # if file not trashed and previous file(or root for first
            # file) in parents then remember file id
            if not f['labels']['trashed'] and \
                    any([file_id in parent['id'] for parent in f['parents']]):
                file_id = f['id']
                file_exists = True
                break
        #  else error
        if not file_exists:
            if write_access == True:
                body = {
                    'mimeType': f_types[idx],
                    'title': name,
                    'parents': [{"id": file_id}]
                }
                file_id = service.files().insert(
                    body=body).execute(http=http)['id']
            else:
                return None
    return file_id


def get_worksheet(gc, gfile_id, wks_name, write_access=False, new_sheet_dimensions=(1000,100)):
    """DOCS..."""
    if wks_name is not None:
        wsheet_match = lambda wks: re.match(
            r"<Worksheet '%s' id:\S+>" % (wks_name), str(wks))
    try:
        spsh = gc.open_by_key(gfile_id)
        wkss = spsh.worksheets()
        # if worksheet name is not provided , take first worksheet
        if wks_name is None:
            wks = spsh.sheet1
        # if worksheet name provided and exist in given spreadsheet
        elif any(map(wsheet_match, wkss)):
            wks = spsh.worksheet(wks_name)
        else:
            if write_access == True:
                #rows, cols = new_sheet_dimensions
                wks = spsh.add_worksheet(wks_name, *new_sheet_dimensions)
            else:
                wks = None
    except gspread.httpsession.HTTPError as e:
        logr.error('Status:', e.response.status)
        logr.error('Reason:', e.response.reason)
        raise

    return wks


def delete_file(credentials, file_id):
    """DOCS..."""
    try:
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v2', http=http)
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError as e:
        logr.error('Status:', e)
        raise
