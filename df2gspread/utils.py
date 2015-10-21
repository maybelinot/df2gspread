#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-11 10:57:06
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2015-10-01 12:44:06

from __future__ import unicode_literals, absolute_import

import logging
import os
import subprocess
import sys

from oauth2client import file, client, tools

# Load logging before anything else
logging.basicConfig(format='>> %(message)s')
logr = logging.getLogger('members')

''' Load the file with credentials '''
CLIENT_SECRET_FILE = os.path.expanduser('~/.gdrive_private')

DEFAULT_TOKEN = os.path.expanduser('~/.oauth/drive.json')

# FIXME: clarify scopes
SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
          'https://www.googleapis.com/auth/drive '
          'https://spreadsheets.google.com/feeds '
          'https://docs.google.com/feeds')


DEFAULT_TOKEN = os.path.expanduser('~/.oauth/drive.json')


SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
          'https://www.googleapis.com/auth/drive '
          'https://spreadsheets.google.com/feeds '
          'https://docs.google.com/feeds')


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
            parents=[tools.argparser]).parse_known_args()[0]
    except ImportError:
        flags = None
        logr.error(
            'Unable to parse oauth2client args; `pip install argparse`')


    store = file.Storage(DEFAULT_TOKEN)

    credentials = store.get()
    if not credentials or credentials.invalid:

        flow = client.flow_from_clientsecrets(
            CLIENT_SECRET_FILE, SCOPES)
        flow.redirect_uri = client.OOB_CALLBACK_URN
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        logr.info('Storing credentials to ' + DEFAULT_TOKEN)

    return credentials
