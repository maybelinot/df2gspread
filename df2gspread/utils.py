#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

# PY3 COMPAT
from __future__ import unicode_literals, absolute_import

import logging
import os
import subprocess
import sys

# Load logging before anything else
logging.basicConfig(format='>> %(message)s')
logr = logging.getLogger('members')

''' Load the file with credentials '''
CLIENT_SECRET_FILE = os.path.expanduser('~/.df2gspread')