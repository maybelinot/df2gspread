#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-11 10:57:06
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-19 14:27:12


import logging
import os
import subprocess
import sys
import json

from oauth2client import file, client, tools

# Load logging before anything else
logr = logging.getLogger('df2gspread')

''' Load the file with credentials '''
CLIENT_SECRET_FILE = os.path.join( os.path.expanduser("~"), ".gdrive_private")

DEFAULT_TOKEN = os.path.join( os.path.expanduser("~"), ".oauth", "drive.json")

# FIXME: clarify scopes
SCOPES = ('https://www.googleapis.com/auth/drive.metadata.readonly '
          'https://www.googleapis.com/auth/drive '
          'https://spreadsheets.google.com/feeds '
          'https://docs.google.com/feeds')


def get_credentials(credentials=None, client_secret_file=CLIENT_SECRET_FILE, refresh_token=None):
    """Consistently returns valid credentials object.

    See Also:
        https://developers.google.com/drive/web/quickstart/python

    Args:
        client_secret_file (str): path to client secrets file, defaults to .gdrive_private
        refresh_token (str): path to a user provided refresh token that is already
            pre-authenticated
        credentials (`~oauth2client.client.OAuth2Credentials`, optional): handle direct
            input of credentials, which will check credentials for valid type and
            return them

    Returns:
        `~oauth2client.client.OAuth2Credentials`: google credentials object

    """

    # if the utility was provided credentials just return those
    if credentials:
        if _is_valid_credentials(credentials):
            # auth for gspread
            return credentials
        else:
            print("Invalid credentials supplied. Will generate from default token.")

    token = refresh_token or DEFAULT_TOKEN
    dir_name = os.path.dirname(DEFAULT_TOKEN)
    try:
        os.makedirs(dir_name)
    except OSError:
        if not os.path.isdir(dir_name):
            raise
    store = file.Storage(token)
    credentials = store.get()

    try:
        import argparse
        flags = argparse.ArgumentParser(
            parents=[tools.argparser]).parse_known_args()[0]
    except ImportError:
        flags = None
        logr.error(
            'Unable to parse oauth2client args; `pip install argparse`')

    if not credentials or credentials.invalid:

        flow = client.flow_from_clientsecrets(
            client_secret_file, SCOPES)
        flow.redirect_uri = client.OOB_CALLBACK_URN
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        logr.info('Storing credentials to ' + DEFAULT_TOKEN)

    return credentials


def _is_valid_credentials(credentials):
    return isinstance(credentials, client.OAuth2Credentials)


def create_service_credentials(private_key_file=None, client_email=None,
                               client_secret_file=CLIENT_SECRET_FILE):
    """Create credentials from service account information.

    See Also:
        https://developers.google.com/api-client-library/python/auth/service-accounts

    Args:
        client_secret_file (str): path to json file with just the client_email when
            providing the `private_key_file` separately, or this file can have both the
            `client_email` and `private_key` contained in it. Defaults to .gdrive_private
        client_email (str): service email account
        private_key_file (str): path to the p12 private key, defaults to same name of file
            used for regular authentication

    Returns:
        `~oauth2client.client.OAuth2Credentials`: google credentials object

    """
    if private_key_file is not None:
        with open(os.path.expanduser(private_key_file)) as f:
            private_key = f.read()
    else:
        private_key = None

    if client_email is None:
        with open(os.path.expanduser(client_secret_file)) as client_file:
            client_data = json.load(client_file)

            if 'installed' in client_data:

                # handle regular json format where key is separate
                client_email = client_data['installed']['client_id']
                if private_key is None:
                    raise RuntimeError('You must have the private key file \
                                       with the regular json file. Try creating a new \
                                       public/private key pair and downloading as json.')
            else:
                # handle newer case where json file has everything in it
                client_email = client_data['client_email']
                private_key = client_data['private_key']

    if client_email is None or private_key is None:
        raise RuntimeError(
            'Client email and/or private key not provided by inputs.')

    credentials = client.SignedJwtAssertionCredentials(
        client_email, private_key, SCOPES)

    return credentials
