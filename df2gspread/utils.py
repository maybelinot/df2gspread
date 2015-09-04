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

import oauth2client

# Load logging before anything else
logging.basicConfig(format='>> %(message)s')
logr = logging.getLogger('members')

''' Load the file with credentials '''
CLIENT_SECRET_FILE = os.path.expanduser('~/.df2gspread')


def run(cmd):
    cmd = cmd if isinstance(cmd, list) else cmd.split()
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as error:
        logr.error("'{0}' failed: {1}".format(cmd, error))
        raise
    output, errors = process.communicate()
    if process.returncode != 0 or errors:
        if output:
            logr.error(output)
        if errors:
            logr.error(errors)
        sys.exit(process.returncode)
    return output, errors


def get_credentials():
    """
    FIXME DOCs
    Taken from:
    https://developers.google.com/drive/web/quickstart/python
    """
    try:
        import argparse
        flags = argparse.ArgumentParser(
            parents=[oauth2client.tools.argparser]).parse_args()
    except ImportError:
        logr.error(
            'Unable to parse oauth2client args; `pip install argparse` required')
        flags = None
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:

        flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        if flags:
            credentials = oauth2client.tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = oauth2client.tools.run(flow, store)
        logr.info('Storing credentials to ' + credential_path)
    return credentials