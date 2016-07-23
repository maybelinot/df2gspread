#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:28:21
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-03-08 12:35:42


from string import ascii_uppercase
from itertools import islice

import pandas as pd
import gspread
import re

from .utils import get_credentials
from .gfiles import get_file_id, get_worksheet

try:
    input = raw_input
except NameError:  # Python 3
    pass


def upload(df, gfile="/New Spreadsheet", wks_name=None, chunk_size=1000,
           col_names=True, row_names=True, clean=True, credentials=None,
           start_cell = 'A1'):
    '''
        Upload given Pandas DataFrame to Google Drive and returns 
        gspread Worksheet object

        :param df: Pandas DataFrame
        :param gfile: path to Google Spreadsheet or gspread ID
        :param wks_name: worksheet name
        :param chunk_size: size of chunk to upload
        :param col_names: passing top row to column names for Pandas DataFrame
        :param row_names: passing left column to row names for Pandas DataFrame
        :param clean: clean all data in worksheet before uploading 
        :param credentials: provide own credentials
        :type df: class 'pandas.core.frame.DataFrame'
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

    wks = get_worksheet(gc, gfile_id, wks_name, write_access=True)
    if clean:
        wks = clean_worksheet(wks, gfile_id, wks_name, credentials)

    start_col = re.split('(\d+)',start_cell)[0].upper()
    start_row = re.split('(\d+)',start_cell)[1]

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    last_idx = len(df.index) if col_names else len(df.index) - 1
    last_idx_adjust = int(start_row) - 1
    last_idx = last_idx + last_idx_adjust

    seq_num = len(df.columns) if row_names else len(df.columns) - 1
    seq_adjust = 0
    for count, letter in enumerate(start_col):
        seq_adjust = ord(letter.upper()) - 65 + (count*26) + seq_adjust
    seq_num = seq_num + seq_adjust

    last_col = ''
    while seq_num >= 0:
        last_col = ascii_uppercase[seq_num % len(ascii_uppercase)] + last_col
        seq_num = seq_num // len(ascii_uppercase) - 1

    # if pandas df large than given worksheet then increase num of cols or rows
    if len(df.index) + 1 + last_idx_adjust > wks.row_count:
        wks.add_rows(len(df.index) - wks.row_count + 1 + last_idx_adjust)

    if len(df.columns) + 1 + seq_adjust > wks.col_count:
        wks.add_cols(len(df.columns) - wks.col_count + 1 + seq_adjust)

    # Define first cell for rows and columns
    first_col = start_col[:-1] + chr(ord(start_col[-1]) + 1) + start_row if row_names else start_col + start_row
    first_row = start_col + str(int(start_row) + 1) if col_names else start_col + start_row

    # Addition of col names
    if col_names:
        cell_list = wks.range('%s:%s%s' % (first_col, last_col, start_row))
        for idx, cell in enumerate(cell_list):
            cell.value = df.columns.values[idx]
        wks.update_cells(cell_list)

    # Addition of row names
    if row_names:
        cell_list = wks.range('%s:%s%d' % (first_row, start_col, last_idx + 1))
        for idx, cell in enumerate(cell_list):
            cell.value = df.index[idx]
        wks.update_cells(cell_list)

    # Addition of cell values
    cell_list = wks.range('%s%s:%s%d' % (
        re.split('(\d+)',first_col)[0], re.split('(\d+)',first_row)[1], last_col, last_idx + 1))
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


def clean_worksheet(wks, gfile_id, wks_name, credentials):
    """DOCS..."""

    values = wks.get_all_values()
    if values:
        df_ = pd.DataFrame(index=range(len(values)),
                           columns=range(len(values[0])))
        df_ = df_.fillna('')
        wks = upload(df_, gfile_id, wks_name=wks_name,
                     col_names=False, row_names=False, clean=False,
                     credentials=credentials)
    return wks
