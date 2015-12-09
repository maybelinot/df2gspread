#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:54:47
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2015-12-09 19:26:30

import re
import httplib2

from apiclient import discovery
import gspread


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
            # if file not trashed and previos file(or root for first
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


def get_worksheet(gc, gfile_id, wks_name, write_access=False):
    """DOCS..."""
    if wks_name is not None:
        wsheet_match = lambda wks: re.match(
            r"<Worksheet '%s' id:\S+>" % (wks_name), str(wks))
    try:
        spsh = gc.open_by_key(gfile_id)
        wkss = spsh.worksheets()
        # if worksheet name is not provided , take first worksheet
        if wks_name is None:
            if write_access == True:
                wks = clear_worksheet(spsh)
            else:
                wks = spsh.sheet1
        # if worksheet name provided and exist in given spreadsheet
        elif any(map(wsheet_match, wkss)):
            if write_access == True:
                wks = clear_worksheet(spsh, wks_name)
            else:
                wks = spsh.worksheet(wks_name)
        else:
            if write_access == True:
                wks = spsh.add_worksheet(wks_name, 1000, 100)
            else:
                wks = None
    except gspread.httpsession.HTTPError as e:
        logr.error('Status:', e.response.status)
        logr.error('Reason:', e.response.reason)
        raise

    return wks


def clear_worksheet(spsh, wks_name=None):
    """DOCS..."""
    tmp_wks = None

    wkss = spsh.worksheets()
    if len(wkss) == 1:
        tmp_wks = spsh.add_worksheet('tmp', 1, 1)
    if wks_name:
        wks = spsh.worksheet(wks_name)
    else:
        wks = spsh.sheet1

    spsh.del_worksheet(wks)
    if wks_name:
        wks = spsh.add_worksheet(wks_name, 1000, 100)
    else:
        wks = spsh.add_worksheet('Sheet1', 1000, 100)

    if tmp_wks:
        spsh.del_worksheet(tmp_wks)

    return wks


def delete_file(credentials, file_id):
    """DOCS..."""
    try:
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v2', http=http)
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError, error:
        raise RuntimeError('An error occurred: %s' % error)
