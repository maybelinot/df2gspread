#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-04 14:04:46
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-01-19 14:54:20


# python-2.7 setup.py build



from setuptools import setup

VERSION_FILE = "df2gspread/_version.py"
VERSION_EXEC = ''.join(open(VERSION_FILE).readlines())
__version__ = ''
exec(str(VERSION_EXEC))  # update __version__
if not __version__:
    raise RuntimeError("Unable to find version string in %s." % VERSION_FILE)

# acceptable version schema: major.minor[.patch][-sub[ab]]
__pkg__ = 'df2gspread'
__pkgdir__ = {'df2gspread': 'df2gspread'}
__pkgs__ = ['df2gspread']
__desc__ = 'Export tables to Google Spreadsheets.'
__scripts__ = ['bin/csv2gspread']
__irequires__ = [
    # CORE DEPENDENCIES
    'argparse>=1.3.0',
    'google-api-python-client==1.6.7',
    'gspread>=2.1.1',
    'oauth2client>=1.5.0,<5.0.0dev',
    'pandas',
    'pycrypto'
]
__xrequires__ = {
    'tests': [
        'pytest==2.7.2',
        # 'instructions',
        # 'pytest-pep8==1.0.6',  # run with `py.test --pep8 ...`
    ],
    # 'docs': ['sphinx==1.3.1', ],
    # 'github': ['PyGithub==1.25.2', ],
    # 'invoke': ['invoke==0.10.1', ],
}

pip_src = 'https://pypi.python.org/packages/src'
__deplinks__ = []

# README is in the parent directory
readme_pth = 'README.rst'
with open(readme_pth) as _file:
    readme = _file.read()

github = 'https://github.com/maybelinot/df2gspread'
download_url = '%s/archive/master.zip' % github

default_setup = dict(
    url=github,
    license='GPLv3',
    author='Eduard Trott',
    author_email='etrott@redhat.com',
    maintainer='Chris Ward',
    maintainer_email='cward@redhat.com',
    download_url=download_url,
    long_description=readme,
    data_files=[],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        'Topic :: Utilities',
    ],
    keywords=['information'],
    dependency_links=__deplinks__,
    description=__desc__,
    install_requires=__irequires__,
    extras_require=__xrequires__,
    name=__pkg__,
    package_dir=__pkgdir__,
    packages=__pkgs__,
    scripts=__scripts__,
    version=__version__,
    zip_safe=False,
)

setup(**default_setup)
