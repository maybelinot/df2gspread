#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 13:25:41
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2015-09-16 14:46:02


from __future__ import absolute_import

import pytest


# MAKE THIS SO IT ONLY EVER GETS RUN ONCE PER "SESSION"
def test_global_import():
    from df2gspread import df2gspread


@pytest.mark.xfail(reason="Credentials")
def test_spreadsheet():
    import string
    import random
    import pandas as pd

    from df2gspread import df2gspread as d2g
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    df = pd.DataFrame([1, 2, 3, 4])
    filepath = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    credentials = get_credentials()

    # creation of new spreadsheet
    d2g.upload(df, filepath)

    # updating existed spreadsheet by filepath
    df = pd.DataFrame([1, 2, 3, 4, 5])
    d2g.upload(df, filepath)

    # updating existed spreadsheet by file_id
    file_id = get_file_id(credentials, filepath)
    d2g.upload(df, file_id)

    # Clear created file from drive
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    delete_file(credentials, file_id)


@pytest.mark.xfail(reason="Credentials")
def test_worksheet():
    import string
    import random
    import pandas as pd

    from df2gspread import df2gspread as d2g
    from df2gspread import gspread2df as g2d
    from df2gspread.utils import get_credentials
    from df2gspread.gfiles import get_file_id
    from df2gspread.gfiles import delete_file

    df_upload = pd.DataFrame(
        {'0': ['1', '2', '3', '4']}, index=['1', '2', '3', '4'])

    filepath = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    # First worksheet as default
    d2g.upload(df_upload, filepath)
    df_download = g2d.download(filepath, col_names=True, row_names=True)
    assert all(df_upload == df_download)

    # updating existed spreadsheet
    d2g.upload(df_upload, filepath, wks_name=filepath)
    df_download = g2d.download(filepath, col_names=True, row_names=True)
    assert all(df_upload == df_download)

    # Clear created file from drive
    credentials = get_credentials()
    file_id = get_file_id(credentials, filepath)
    delete_file(credentials, file_id)

if __name__ == "__main__":
    test_worksheet()
