#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:45:16
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-18 13:20:56


import os
import sys
from string import ascii_uppercase

import gspread
import pandas as pd
import numpy as np

from .utils import logr, get_credentials
from .gfiles import get_file_id, get_worksheet

# FIXME: clarify scopes
SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
          'https://www.googleapis.com/auth/drive '
          'https://spreadsheets.google.com/feeds '
          'https://docs.google.com/feeds')


def download(gfile, wks_name=None, col_names=False,
             row_names=False, credentials=None):
    """
        Download Google Spreadsheet and convert it to Pandas DataFrame

        :param gfile: path to Google Spreadsheet or gspread ID
        :param wks_name: worksheet name
        :param col_names: assing top row to column names for Pandas DataFrame
        :param row_names: assing left column to row names for Pandas DataFrame
        :param credentials: provide own credentials
        :type gfile: str
        :type wks_name: str
        :type col_names: bool
        :type row_names: bool
        :type credentials: class 'oauth2client.client.OAuth2Credentials'
        :returns: Pandas DataFrame
        :rtype: class 'pandas.core.frame.DataFrame'

        :Example:

            >>> from df2gspread import gspread2df as g2d
            >>> df = g2d.download(gfile="1U-kSDyeD-...", col_names=True, row_names=True)
            >>> df
                   col1 col2
            field1    1    2
            field2    3    4
    """

    # access credentials
    credentials = get_credentials(credentials)
    # auth for gspread
    gc = gspread.authorize(credentials)

    try:
        # if gfile is file_id
        spsh = gc.open_by_key(gfile)
        gfile_id = gfile
    except:
        # else look for file_id in drive
        gfile_id = get_file_id(credentials, gfile)

    if gfile_id is None:
        raise RuntimeError("Spreadsheet '%s' is not exist" % (gfile))

    wks = get_worksheet(gc, gfile_id, wks_name)

    if wks is None:
        raise RuntimeError("Worksheet '%s' is not exist" % (wks_name))

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
        col_names = np.arange(len(raw_data[0]))

    df = pd.DataFrame([pd.Series(row) for row in raw_data], index=row_names)
    df.columns = col_names

    return df
