#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 13:22:22
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2015-09-16 13:23:56


from __future__ import unicode_literals, absolute_import

import pytest


# MAKE THIS SO IT ONLY EVER GETS RUN ONCE PER "SESSION"
def test_global_import():
    from df2gspread import df2gspread

