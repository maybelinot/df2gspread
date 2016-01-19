#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 13:25:41
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-19 14:22:34

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
    _v = '0.1.0'

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
