#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 13:25:41
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-03-08 12:38:03

import pytest


# MAKE THIS SO IT ONLY EVER GETS RUN ONCE PER "SESSION"
def test_global_import():
    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d


def test_version_check():
    from df2gspread import _version

    ######################################################
    # THIS NEEDS TO BE UPDATED EVERY TIME THE MAIN PACKAGE
    # VERSION IS UPDATED!!!
    ######################################################
    _v = '0.2.3'

    if _version.__version__ != _v:
        raise SystemError('SYNC VERSION in tests/test_members.py')


def test_spreadsheet_invalid_file_id(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    from df2gspread import gspread2df as g2d

    with pytest.raises(RuntimeError):
        g2d.download(gfile='invalid_file_id')


def test_worksheet_invalid_name(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import pandas as pd

    from df2gspread import gspread2df as g2d
    from df2gspread import df2gspread as d2g

    filepath = '/df2gspread_tests/invalid_wks_name'
    df_upload = pd.DataFrame(['test'])
    d2g.upload(df_upload, filepath)

    with pytest.raises(RuntimeError):
        g2d.download(gfile=filepath, wks_name='invalid_wks_name')


def test_worksheet(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import string
    import random
    import numpy as np
    import pandas as pd
    from pandas.util.testing import assert_frame_equal

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    df_upload = pd.DataFrame(
        {0: ['1', '2', 'x', '4']},
        index=[0, 1, 2, 3])

    filepath = '/df2gspread_tests/' + ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))

    # First worksheet as default
    d2g.upload(df_upload, filepath)
    df_download = g2d.download(filepath, col_names=True, row_names=True)
    df_download.columns = df_download.columns.astype(np.int64)
    df_download.index = df_download.index.astype(np.int64)
    assert_frame_equal(df_upload, df_download)

    # Updating existed spreadsheet
    d2g.upload(df_upload, filepath, wks_name='Sheet2')
    df_download = g2d.download(filepath, col_names=True, row_names=True)
    df_download.columns = df_download.columns.astype(np.int64)
    df_download.index = df_download.index.astype(np.int64)
    assert_frame_equal(df_upload, df_download)

    # Updating with file_id
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    d2g.upload(df_upload, file_id)
    df_download = g2d.download(file_id, col_names=True, row_names=True)
    df_download.columns = df_download.columns.astype(np.int64)
    df_download.index = df_download.index.astype(np.int64)
    assert_frame_equal(df_upload, df_download)

    # Only row_names
    wks = d2g.upload(df_upload, filepath, col_names=False)
    df_download = g2d.download(filepath, row_names=True)
    df_download.index = df_download.index.astype(np.int64)
    # df_download.columns = df_download.columns.astype(np.int64)

    assert_frame_equal(df_upload, df_download)

    # Only col_names
    wks = d2g.upload(df_upload, filepath, row_names=False)
    df_download = g2d.download(filepath, col_names=True)
    df_download.columns = df_download.columns.astype(np.int64)

    assert_frame_equal(df_upload, df_download)

    # Without column or row names
    wks = d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    df_download = g2d.download(filepath)

    assert_frame_equal(df_upload, df_download)

    # Clear created file from drive
    delete_file(credentials, file_id)


def test_gspread2df_start_cell(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import string
    import random
    import numpy as np
    import pandas as pd
    from numpy.testing import assert_array_equal
    from pandas.util.testing import assert_frame_equal

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    filepath = '/df2gspread_tests/' + ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))

    df_upload = pd.DataFrame(
        {0: ['1', '2', 'x', '4'],
        1: ['2', '2', 'y', '4'],
        2: ['3', '2', 'w', '4'],
        3: ['4', '2', 'z', '4']},
        index=[0, 1, 2, 3])

    # Start cell out of the table size
    d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    with pytest.raises(RuntimeError):
        df_download = g2d.download(filepath, start_cell='A5')

    with pytest.raises(RuntimeError):
        df_download = g2d.download(filepath, start_cell='E1')

    # Should be fixed in gspread
    # with pytest.raises(RuntimeError):
    #     df_download = g2d.download(filepath, start_cell='A0')

    # start_cell = 'A3'
    d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    df_download = g2d.download(filepath, start_cell='A3')
    assert_array_equal(df_upload.iloc[2:,:], df_download)

    # start_cell = 'B3'
    d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    df_download = g2d.download(filepath, start_cell='B3')
    assert_array_equal(df_upload.iloc[2:,1:], df_download)

    # Clear created file from drive
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    delete_file(credentials, file_id)


def test_big_worksheet(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import string
    import random
    import numpy as np
    import pandas as pd
    from pandas.util.testing import assert_frame_equal

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    filepath = '/df2gspread_tests/' + ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))

    # Indexes count out of default 1000
    df_upload = pd.DataFrame(index=range(1001),
                             columns=range(2))
    df_upload = df_upload.fillna('0')
    d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    df_download = g2d.download(filepath)
    # df_download.columns = df_download.columns.astype(np.int64)

    assert_frame_equal(df_upload, df_download)

    # Columns count out of default 100
    df_upload = pd.DataFrame(index=range(1),
                             columns=range(101))
    df_upload = df_upload.fillna('0')
    d2g.upload(df_upload, filepath, row_names=False, col_names=False)
    df_download = g2d.download(filepath)
    # df_download.columns = df_download.columns.astype(np.int64)

    assert_frame_equal(df_upload, df_download)

    # Clear created file from drive
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    delete_file(credentials, file_id)


def test_df2gspread_start_cell(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import string
    import random
    import numpy as np
    import pandas as pd
    from pandas.util.testing import assert_frame_equal

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    filepath = '/df2gspread_tests/' + ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))

    df_upload_0 = pd.DataFrame(
        {0: ['1', '2', 'x', '4']},
        index=[0, 1, 2, 3])

    d2g.upload(df_upload_0, filepath, row_names=False, col_names=False, start_cell='A1')
    df_download = g2d.download(filepath)
    df_upload = df_upload_0
    assert_frame_equal(df_upload, df_download)

    d2g.upload(df_upload_0, filepath, row_names=False, col_names=False, start_cell='A2')
    df_download = g2d.download(filepath)
    df_upload = df_upload_0
    new_rows = 1
    new_rows_array = np.chararray((new_rows, len(df_upload.columns)))
    new_rows_array[:] = ''
    df_new_rows = pd.DataFrame(data = new_rows_array)
    df_upload = df_new_rows.append(df_upload, ignore_index=True)
    assert_frame_equal(df_upload, df_download)

    d2g.upload(df_upload_0, filepath, row_names=False, col_names=False, start_cell='B1')
    df_download = g2d.download(filepath)
    df_upload = df_upload_0
    df_upload.insert(0, '-1', '')
    df_upload.columns = range(0, len(df_upload.columns))
    assert_frame_equal(df_upload, df_download)

    d2g.upload(df_upload_0, filepath, row_names=False, col_names=False, start_cell='AB10')
    df_download = g2d.download(filepath)
    df_upload = df_upload_0
    new_cols = 27
    new_cols_array = np.chararray((len(df_upload), new_cols))
    new_cols_array[:] = ''
    df_new_cols = pd.DataFrame(data = new_cols_array)
    df_upload = pd.concat([df_new_cols, df_upload], axis=1)
    df_upload.columns = range(0, len(df_upload.columns))
    new_rows = 9
    new_rows_array = np.chararray((new_rows, len(df_upload.columns)))
    new_rows_array[:] = ''
    df_new_rows = pd.DataFrame(data = new_rows_array)
    df_upload = df_new_rows.append(df_upload, ignore_index=True)
    assert_frame_equal(df_upload, df_download)

    # Backward compatibility df2gspread => gspread2df
    d2g.upload(df_upload_0, filepath, row_names=False, col_names=False, start_cell='AB10')
    df_upload = df_upload_0
    df_download = g2d.download(filepath, start_cell='AB10')
    assert_frame_equal(df_upload, df_download)

    d2g.upload(df_upload_0, filepath, start_cell='AB10')
    df_upload = df_upload_0
    df_download = g2d.download(filepath, row_names=True, col_names=True, start_cell='AB10')
    df_download.index = df_download.index.astype(np.int64)
    df_download.columns = df_download.columns.astype(np.int64)
    assert_frame_equal(df_upload, df_download)

    # Clear created file from drive
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    delete_file(credentials, file_id)

def test_df2gspread_df_size(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    import string
    import random
    import numpy as np
    import pandas as pd
    import gspread
    from pandas.util.testing import assert_frame_equal, assert_equal

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id, delete_file, get_worksheet

    filepath = '/df2gspread_tests/' + ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    gfile_id = get_file_id(credentials, filepath, write_access=True)

    df_upload_a = pd.DataFrame(
        {0: ['1', '2', 'x', '4']},
        index=[0, 1, 2, 3])

    df_upload_b = pd.DataFrame(data = np.array([np.arange(1500)]*2).T).applymap(str)

    #Uploading a small DF to new sheet to test for sizing down from default
    d2g.upload(df_upload_a, filepath, "test1", row_names=False, col_names=False, df_size=True)
    df_download = g2d.download(filepath, "test1")
    df_upload = df_upload_a
    wks = get_worksheet(gc, gfile_id, "test1")
    assert_equal(wks.row_count, len(df_upload))
    assert_equal(len(df_upload.columns), wks.col_count)
    assert_equal(len(df_download), len(df_upload))
    assert_frame_equal(df_upload, df_download)

    #Upload a large DF to existing, smaller sheet to test for proper expansion
    d2g.upload(df_upload_b, filepath, "test1", row_names=False, col_names=False, df_size=True)
    df_download = g2d.download(filepath, "test1")
    df_upload = df_upload_b
    wks = get_worksheet(gc, gfile_id, "test1")
    assert_equal(wks.row_count, len(df_upload))
    assert_equal(len(df_upload.columns), wks.col_count)
    assert_equal(len(df_download), len(df_upload))
    assert_frame_equal(df_upload, df_download)

    #Uploading a small DF to existing large sheet to test for sizing down from default
    d2g.upload(df_upload_a, filepath, "test1", row_names=False, col_names=False, df_size=True)
    df_download = g2d.download(filepath, "test1")
    df_upload = df_upload_a
    wks = get_worksheet(gc, gfile_id, "test1")
    assert_equal(wks.row_count, len(df_upload))
    assert_equal(len(df_upload.columns), wks.col_count)
    assert_equal(len(df_download), len(df_upload))
    assert_frame_equal(df_upload, df_download)

    #New sheet with col names, make sure 1 extra row and column
    d2g.upload(df_upload_a, filepath, "test2", row_names=True, col_names=True, df_size=True)
    df_download = g2d.download(filepath, "test2")
    df_upload = df_upload_a
    wks = get_worksheet(gc, gfile_id, "test2")
    assert_equal(wks.row_count, len(df_upload) + 1)
    assert_equal(len(df_upload.columns) + 1, wks.col_count)
    assert_equal(len(df_download), len(df_upload) + 1)

    #Upload to new sheet with specified dimensions
    d2g.upload(df_upload_a, filepath, "test3", row_names=False, col_names=False, new_sheet_dimensions=(100,10))
    df_download = g2d.download(filepath, "test3")
    df_upload = df_upload_a
    wks = get_worksheet(gc, gfile_id, "test3")
    assert_equal(wks.row_count, 100)
    assert_equal(10, wks.col_count)
    assert_frame_equal(df_upload, df_download)

    #Test df_size with start_cell
    d2g.upload(df_upload_a, filepath, "test4", row_names=False, col_names=False, start_cell='AB10',
        df_size = True)
    df_download = g2d.download(filepath, "test4")
    df_upload = df_upload_a
    new_cols = 27
    new_cols_array = np.chararray((len(df_upload), new_cols))
    new_cols_array[:] = ''
    df_new_cols = pd.DataFrame(data = new_cols_array)
    df_upload = pd.concat([df_new_cols, df_upload], axis=1)
    df_upload.columns = range(0, len(df_upload.columns))
    new_rows = 9
    new_rows_array = np.chararray((new_rows, len(df_upload.columns)))
    new_rows_array[:] = ''
    df_new_rows = pd.DataFrame(data = new_rows_array)
    df_upload = df_new_rows.append(df_upload, ignore_index=True)
    wks = get_worksheet(gc, gfile_id, "test4")
    assert_equal(wks.row_count, len(df_upload))
    assert_equal(len(df_upload.columns), wks.col_count)
    assert_equal(len(df_download), len(df_upload))
    assert_frame_equal(df_upload, df_download)

    #Test df_size with start_cell and sheet dimensions which need to be expanded
    d2g.upload(df_upload_a, filepath, "test5", row_names=False, col_names=False, start_cell='AB10',
        df_size = True, new_sheet_dimensions = (10,27))
    df_download = g2d.download(filepath, "test5")
    df_upload = df_upload_a
    new_cols = 27
    new_cols_array = np.chararray((len(df_upload), new_cols))
    new_cols_array[:] = ''
    df_new_cols = pd.DataFrame(data = new_cols_array)
    df_upload = pd.concat([df_new_cols, df_upload], axis=1)
    df_upload.columns = range(0, len(df_upload.columns))
    new_rows = 9
    new_rows_array = np.chararray((new_rows, len(df_upload.columns)))
    new_rows_array[:] = ''
    df_new_rows = pd.DataFrame(data = new_rows_array)
    df_upload = df_new_rows.append(df_upload, ignore_index=True)
    wks = get_worksheet(gc, gfile_id, "test5")
    assert_equal(wks.row_count, len(df_upload))
    assert_equal(len(df_upload.columns), wks.col_count)
    assert_equal(len(df_download), len(df_upload))
    assert_frame_equal(df_upload, df_download)

    # Clear created file from drive
    delete_file(credentials, gfile_id)

def test_delete_file(user_credentials_not_available):
    if user_credentials_not_available:
        pytest.xfail(reason='Credentials')

    from df2gspread.gfiles import delete_file
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id

    # Clear created folder for testing
    credentials = get_credentials()
    file_id = get_file_id(credentials, '/df2gspread_tests')

    delete_file(credentials, file_id)
