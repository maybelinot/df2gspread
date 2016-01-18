
===============
    Install
===============

PIP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic dependencies for buiding/installing pip packages::

    sudo yum install gcc krb5-devel
    sudo yum install python-devel python-pip python-virtualenv

Upgrade to the latest pip/setup/virtualenv installer code::

    sudo pip install --upgrade pip setuptools virtualenv

Install into a python virtual environment (OPTIONAL)::

    virtualenv ~/df2gspread
    source ~/df2gspread/bin/activate

Install df2gspread (sudo required if not in a virtualenv)::

    pip install df2gspread

See the `pypi package index`__ for detailed package information.

__ https://pypi.python.org/pypi/df2gspread