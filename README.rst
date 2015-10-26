.. image:: https://travis-ci.org/maybelinot/df2gspread.png
   :target: https://travis-ci.org/maybelinot/df2gspread

.. image:: https://coveralls.io/repos/maybelinot/df2gspread/badge.svg
  :target: https://coveralls.io/r/maybelinot/df2gspread


INSTALLATION
============
Example install, using VirtualEnv::

    # install/use python virtual environment
    virtualenv ~/virtenv_scratch --no-site-packages

    # activate the virtual environment
    source ~/virtenv_scratch/bin/activate

    # upgrade pip in the new virtenv
    pip install -U pip setuptools

    # install this package in DEVELOPMENT mode
    python setup.py develop

    # or simply install
    # python setup.py install

ACCESS CREDENTIALS
==================
To allow a script to use Google Drive API we need to authenticate our self 
towards Google.  To do so, we need to create a project, describing the tool 
and generate credentials. Please use your web browser and go to 
`Google console <https://console.developers.google.com>`_ and :

* Choose **"Create Project"** in popup menu on the top.

* A dialog box appears, so give your project a name and click on **"Create"** button.

* On the left-side menu click on **"APIs & auth"** ->  **"API"**.

* A table of available APIs is shown. Switch **"Drive API"** and click on **"Enable API"** button. Other APIs might be switched off, for our purpose.

* On the left-side menu click on **"APIS & auth"** -> **"Credentials"**.

* In section **"OAuth consent screen"** select your email address and give your product a name. Then click on **"Save"** button.

* In section **"Credentials"** click on **"Add credentials"** and switch **"OAuth 2.0 client ID"**.

* A dialog box  **"Create Cliend ID"** appears. Select **"Application type"** item as **"Other"**.

* Click on **"Create"** button.

* Click on **"Download JSON"** icon on the right side of created **"OAuth 2.0 client IDs"** and store the downloaded file on your file system. Please be aware, the file contains your private credentials, so take care of the file in the same way you care of your private SSH key; i.e. move downloaded JSON file to **~/.gdrive_private**. 

* Then, the first time you run it your browser window will open a google authorization request page. Approve authorization and then the credentials will work as expected.


USAGE
=====
Run df2gspread like::

    from df2gspread import df2gspread as d2g
    import pandas as pd
    d = [pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
        pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])]
    df = pd.DataFrame(d)
    
    # use full path to spreadsheet file
    spreadsheet = '/some/folder/New Spreadsheet'
    # or spreadsheet file id 
    # spreadsheet = '1cIOgi90...'

    wks_name = 'New Sheet'
    
    d2g.upload(df, spreadsheet, wks_name)
    # if spreadsheet already exists, all data of provided worksheet(or first as default) 
    # will be replaced with data of given DataFrame, make sure that this is what you need!  

Run gspread2df like::

    from df2gspread import gspread2df as g2d
    
    # use full path to spreadsheet file
    spreadsheet = '/some/folder/New Spreadsheet'
    # or spreadsheet file id 
    # spreadsheet = '1cIOgi90...'
    wks_name = 'New Sheet'
    
    df = g2d.download(spreadsheet, wks_name, col_names = True, row_names = True)

DEVELOPMENT
===========
Install the supplied githooks; eg::

    ln -s ~/repos/df2gspread/_githooks/commit-msg ~/repos/df2gspread/.git/hooks/commit-msg
    ln -s ~/repos/df2gspread/_githooks/pre-commit ~/repos/df2gspread/.git/hooks/pre-commit