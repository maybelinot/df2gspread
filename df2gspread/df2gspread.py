#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:28:21
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-18 13:29:59


from string import ascii_uppercase
from itertools import islice

import gspread

from .utils import get_credentials
from .gfiles import get_file_id, get_worksheet

try:
    input = raw_input
except NameError:  # Python 3
    pass


def upload(df, gfile="/New Spreadsheet", wks_name=None, chunk_size=1000,
           col_names=True, row_names=True, clean=True, credentials=True):
    '''
        Upload given Pandas DataFrame to Google Drive and returns 
        gspread Worksheet object

        :param gfile: path to Google Spreadsheet or gspread ID
        :param wks_name: worksheet name
        :param chunk_size: size of chunk to upload
        :param col_names: assing top row to column names for Pandas DataFrame
        :param row_names: assing left column to row names for Pandas DataFrame
        :param clean: clean all data in worksheet before uploading 
        :param credentials: provide own credentials
        :type gfile: str
        :type wks_name: str
        :type chunk_size: int
        :type col_names: bool
        :type row_names: bool
        :type clean: bool
        :type credentials: class 'oauth2client.client.OAuth2Credentials'
        :returns: gspread Worksheet
        :rtype: class 'gspread.models.Worksheet'

        :Example:

            >>> from df2gspread import df2gspread as d2g
            >>> import pandas as pd
            >>> df = pd.DataFrame([1 2 3])
            >>> wks = d2g.upload(df, wks_name='Example worksheet')
            >>> wks.title
            'Example worksheet'
    '''
    # access credentials
    credentials = get_credentials(credentials)
    # auth for gspread
    gc = gspread.authorize(credentials)

    try:
        # if gfile is file_id
        gc.open_by_key(gfile)
        gfile_id = gfile
    except Exception:
        # else look for file_id in drive
        gfile_id = get_file_id(credentials, gfile, write_access=True)

    if clean:
        wks = get_worksheet(gc, gfile_id, wks_name, write_access=True)
    else:
        wks = get_worksheet(gc, gfile_id, wks_name)

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    last_idx = len(df.index) if col_names else len(df.index) - 1

    seq_num = len(df.columns) if row_names else len(df.columns) - 1
    last_col = ''
    while seq_num >= 0:
        last_col = ascii_uppercase[seq_num % len(ascii_uppercase)] + last_col
        seq_num = seq_num // len(ascii_uppercase) - 1

    # if pandas df large then given worksheet then increes num of cols or rows
    if len(df.index) + 1 > wks.row_count:
        wks.add_rows(len(df.index) - wks.row_count + 1)

    if len(df.columns) + 1 > wks.col_count:
        wks.add_cols(len(df.columns) - wks.col_count + 1)

    # Define first cell for rows and columns
    first_col = 'B1' if row_names else 'A1'
    first_row = 'A2' if col_names else 'A1'

    # Addition of col names
    if col_names:
        cell_list = wks.range('%s:%s1' % (first_col, last_col))
        for idx, cell in enumerate(cell_list):
            cell.value = df.columns.values[idx]
        wks.update_cells(cell_list)

    # Addition of row names
    if row_names:
        cell_list = wks.range('%s:A%d' % (first_row, last_idx + 1))
        for idx, cell in enumerate(cell_list):
            cell.value = df.index[idx]
        wks.update_cells(cell_list)

    # Addition of cell values
    cell_list = wks.range('%s%s:%s%d' % (
        first_col[0], first_row[1], last_col, last_idx + 1))
    for j, idx in enumerate(df.index):
        for i, col in enumerate(df.columns.values):
            cell_list[i + j * len(df.columns.values)].value = df[col][idx]
    for cells in grouper(chunk_size, cell_list):
        wks.update_cells(list(cells))

    return wks


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk
