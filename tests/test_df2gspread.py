#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-08 16:29:32
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
<<<<<<< HEAD
# @Last Modified time: 2015-09-15 09:29:57

from __future__ import unicode_literals, absolute_import

import pytest


# MAKE THIS SO IT ONLY EVER GETS RUN ONCE PER "SESSION"
def test_global_import():
    from df2gspread import df2gspread
=======
# @Last Modified time: 2015-09-08 16:33:27

from __future__ import unicode_literals, absolute_import

from instructions import commands, datatypes
import pytest

TEST_REPO = 'maybelinot/df2gspread'


# MAKE THIS SO IT ONLY EVER GETS RUN ONCE PER "SESSION"
def test_global_import():
    from df2gspread import df2gspread 


def test_default_auth_good():
    from df2gspread import df2gspread 

    # DEFAULT AUTH should be 'anonymous'; no user/pass required

    # assignees should not require authenticated user to call
    target = 'assignees'
    users = repo.extract(repo_url=TEST_REPO, target=target)

    # see: https://github.com/maxtepkeev/instructions
    # see: http://bit.ly/maxtepkeev_instructions_eupy15
    result = commands.count(datatypes.string).inside(users)
    if not result >= 1:
        raise RuntimeError(
            "Expeted more than one assignee, got {}".format(result))


def test_default_auth_bad():
    from df2gspread import df2gspread 

    # DEFAULT AUTH should be 'anonymous'; no user/pass required
    # collaborators SHOULD require auth
    target = 'collaborators'
    try:
        repo.extract(repo_url=TEST_REPO, target=target)
    # FIXME: check for specific github exception too.
    except Exception as e:
        print('EXPECTED GITHUB EXCEPTION, got {}. IGNORING!'.format(e))
    else:
        raise RuntimeError("EXPECTED EXCEPTION, didn't get one though... oops")
>>>>>>> Add tests
