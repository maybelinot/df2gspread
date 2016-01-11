# Running Tests

See conftest.py, which sets up some shared data for the tests. The credentials
testing is configured to look for specific files and if those do not exist, then
the test that relies on those credentials will be marked to be expected to fail.

Make sure that if the following files do exist, that the test is not marked to fail
as that suggests that there are issues loading the files in general.


- "Old" style of service credentials: `'~/.df2gspread_secrets.p12'`
- "New" json style: `'~/.gdrive_service_private'`