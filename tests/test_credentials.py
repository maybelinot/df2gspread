
import pytest


def test_client_secrets_credentials(service_credentials,
                                    service_credentials_not_available):

    if service_credentials_not_available:
        pytest.mark.xfail(reason='Service Credentials Not Available')

    from df2gspread.utils import create_service_credentials, _is_valid_credentials

    key_file = service_credentials['key_file']
    client_file = service_credentials['client_file']

    cred = create_service_credentials(private_key_file=key_file, client_email=client_file)

    assert _is_valid_credentials(cred)
