
import pytest
from df2gspread.utils import (get_credentials,
                              create_service_credentials)


@pytest.fixture
def service_credentials():

    sc = dict(key_file='~/.df2gspread_secrets.p12',
              client_file='~/.gdrive_service_private')

    return sc


@pytest.fixture
def user_credentials_not_available():
    try:
        _ = get_credentials()
        should_fail = False
    except Exception:
        should_fail = True

    return should_fail


@pytest.fixture
def service_credentials_not_available(service_credentials):

    key_file = service_credentials['key_file']
    client_email_file = service_credentials['client_file']

    try:
        _ = create_service_credentials(private_key_file=key_file,
                                       client_secret_file=client_email_file)
        should_fail = False
    except Exception:
        should_fail = True

    return should_fail
