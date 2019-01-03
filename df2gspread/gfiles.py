#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2018-05-02 13:53:10
# @Email:  etrott@redhat.com
# @Last Modified by:   maybelinot
# @Last Modified time: 2018-05-02 13:53:10


import re
from httplib2 import Http

from apiclient import discovery, errors
import gspread

from .utils import logr


def get_file_id(credentials, gfile, write_access=False):
    """
        Get file ID by provided path. If file does not exist and
        `write_access` is true, it will create whole path for you.

        :param credentials: provide own credentials
        :param gfile: path to Google Spreadsheet
        :param write_access: allows to create full path if file does not exist
        :type credentials: class 'oauth2client.client.OAuth2Credentials'
        :type gfile: str
        :type write_access: boolean
        :returns: file ID
        :rtype: str

        :Example:

            >>> from df2gspread.gfiles import get_file_id
            >>> from df2gspread.utils import get_credentials
            >>> gfile = '/some/folder/with/file'
            >>> credentials = get_credentials()
            >>> get_file_id(credentials=credentials, gfile=gfile, write_access=True)
            u'78asbcsSND8sdSACNsa7ggcasca8shscaSACVD'
    """
    # auth for apiclient
    http = credentials.authorize(Http())
    service = discovery.build('drive', 'v3', http=http, cache_discovery=False)

    file_id = service.files().get(fileId='root', fields='id').execute().get('id')

    # folder/folder/folder/spreadsheet
    pathway = gfile.strip('/').split('/')

    for idx, name in enumerate(pathway):
        files = service.files().list(
            q="name = '{}' and trashed = false and '{}' in parents".format(name, file_id)).execute()['files']
        if len(files) > 0:
            # Why do you ever need to use several folders with the same name?!
            file_id = files[0].get('id')
        elif write_access == True:
            body = {
                'mimeType': 'application/vnd.google-apps.' + ('spreadsheet' if idx == len(pathway)-1 else 'folder'),
                'name': name,
                'parents': [file_id]
            }
            file_id = service.files().create(body=body, fields='id').execute().get('id')
        else:
            return None
    return file_id


def get_worksheet(gc, gfile_id, wks_name, write_access=False, new_sheet_dimensions=(1000, 100)):
    """DOCS..."""

    spsh = gc.open_by_key(gfile_id)

    # if worksheet name is not provided , take first worksheet
    if wks_name is None:
        wks = spsh.sheet1
    # if worksheet name provided and exist in given spreadsheet
    else:
        try:
            wks = spsh.worksheet(wks_name)
        except:
            #rows, cols = new_sheet_dimensions
            wks = spsh.add_worksheet(
                wks_name, *new_sheet_dimensions) if write_access == True else None

    return wks


def delete_file(credentials, file_id):
    """DOCS..."""
    try:
        http = credentials.authorize(Http())
        service = discovery.build(
            'drive', 'v3', http=http, cache_discovery=False)
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError as e:
        logr.error(e)
        raise
