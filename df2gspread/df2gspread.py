#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:28:21
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-03-08 12:35:42


import pandas as pd
import numpy as np
import gspread
import re

from .utils import get_credentials
from .gfiles import get_file_id, get_worksheet

try:
    input = raw_input
except NameError:  # Python 3
    pass


def upload(df, gfile="/New Spreadsheet", wks_name=None,
           col_names=True, row_names=True, clean=True, credentials=None,
           start_cell = 'A1', df_size = False, new_sheet_dimensions = (1000,100)):
    '''
        Upload given Pandas DataFrame to Google Drive and returns
        gspread Worksheet object

        :param df: Pandas DataFrame
        :param gfile: path to Google Spreadsheet or gspread ID
        :param wks_name: worksheet name
        :param col_names: passing top row to column names for Pandas DataFrame
        :param row_names: passing left column to row names for Pandas DataFrame
        :param clean: clean all data in worksheet before uploading
        :param credentials: provide own credentials
        :param start_cell: specify where to insert the DataFrame; default is A1
        :param df_size:
            -If True and worksheet name does NOT exist, will create
            a new worksheet that is the size of the df; otherwise, by default,
            creates sheet of 1000x100 cells.
            -If True and worksheet does exist, will resize larger or smaller to
            fit new dataframe.
            -If False and dataframe is larger than existing sheet, will resize
            the sheet larger.
            -If False and dataframe is smaller than existing sheet, does not resize.
        :param new_sheet_dimensions: tuple of (row, cols) for size of a new sheet
        :type df: class 'pandas.core.frame.DataFrame'
        :type gfile: str
        :type wks_name: str
        :type col_names: bool
        :type row_names: bool
        :type clean: bool
        :type credentials: class 'oauth2client.client.OAuth2Credentials'
        :type start_cell: str
        :type df_size: bool
        :type new_sheet_dimensions: tuple
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
        gc.open_by_key(gfile).__repr__()
        gfile_id = gfile
    except:
        gfile_id = get_file_id(credentials, gfile, write_access=True)

    # Tuple of rows, cols in the dataframe.
    # If user did not explicitly specify to resize sheet to dataframe size
    # then for new sheets set it to new_sheet_dimensions, which is by default 1000x100
    if df_size:
        new_sheet_dimensions = (len(df), len(df.columns))
    wks = get_worksheet(gc, gfile_id, wks_name, write_access=True,
        new_sheet_dimensions=new_sheet_dimensions)
    if clean:
        wks = clean_worksheet(wks, gfile_id, wks_name, credentials)

    start_col = re.split(r'(\d+)',start_cell)[0].upper()
    start_row = re.split(r'(\d+)',start_cell)[1]
    start_row_int, start_col_int = gspread.utils.a1_to_rowcol(start_cell)

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    num_rows = len(df.index) + 1 if col_names else len(df.index)
    last_idx_adjust = start_row_int - 1
    last_idx = num_rows + last_idx_adjust

    num_cols = len(df.columns) + 1 if row_names else len(df.columns)
    last_col_adjust = start_col_int - 1
    last_col_int = num_cols + last_col_adjust
    last_col = re.split(r'(\d+)',(gspread.utils.rowcol_to_a1(1, last_col_int)))[0].upper()

    # If user requested to resize sheet to fit dataframe, go ahead and
    # resize larger or smaller to better match new size of pandas dataframe.
    # Otherwise, leave it the same size unless the sheet needs to be expanded
    # to accomodate a larger dataframe.
    if df_size:
        wks.resize(rows=len(df.index) + col_names, cols=len(df.columns) + row_names)
    if len(df.index) + col_names + last_idx_adjust > wks.row_count:
        wks.add_rows(len(df.index) - wks.row_count + col_names + last_idx_adjust)
    if len(df.columns) + row_names + last_col_adjust  > wks.col_count:
        wks.add_cols(len(df.columns) - wks.col_count + row_names + last_col_adjust)

    # Define first cell for rows and columns
    first_col = re.split(r'(\d+)',(gspread.utils.rowcol_to_a1(1, start_col_int + 1)))[0].upper() if row_names else start_col
    first_row = str(start_row_int + 1) if col_names else start_row

    # Addition of col names
    if col_names:
        cell_list = wks.range('%s%s:%s%s' % (first_col, start_row, last_col, start_row))
        for idx, cell in enumerate(cell_list):
            cell.value = df.columns.astype(str)[idx]
        wks.update_cells(cell_list)

    # Addition of row names
    if row_names:
        cell_list = wks.range('%s%s:%s%d' % (
            start_col, first_row, start_col, last_idx))
        for idx, cell in enumerate(cell_list):
            cell.value = df.index.astype(str)[idx]
        wks.update_cells(cell_list)


    # convert df values to string
    df = df.applymap(str)
    # Addition of cell values
    cell_list = wks.range('%s%s:%s%d' % (
        first_col, first_row, last_col, last_idx))
    for j, idx in enumerate(df.index):
        for i, col in enumerate(df.columns.values):
            if not pd.isnull(df[col][idx]):
                cell_list[i + j * len(df.columns.values)].value = df[col][idx]

    wks.update_cells(cell_list)
    return wks

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
