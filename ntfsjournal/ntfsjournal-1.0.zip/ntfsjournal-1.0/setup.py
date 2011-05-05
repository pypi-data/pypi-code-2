#!/usr/bin/env python
from distutils.core import setup, Extension
setup(
    name = 'ntfsjournal',
    ext_modules=[Extension('ntfsjournal', ['pyNTFSjournal.cpp'])],
    version = '1.0',
    description = 'Module to read NTFS USN journal.',
    author='Lazar Laszlo',
    author_email='laszlolazar@yahoo.com',
    url='http://pyntfsjournal.sourceforge.net',
    download_url='http://pyntfsjournal.sourceforge.net',
    long_description="""Example:

import ntfsjournal
ntfsjournal.get('c', ntfsjournal.USN_REASON_FILE_DELETE)

The above script will get the delete journal for drive C.

Other filters:

ntfsjournal.USN_REASON_ALL
ntfsjournal.USN_REASON_CLOSE
ntfsjournal.USN_REASON_DATA_EXTEND
ntfsjournal.USN_REASON_DATA_OVERWRITE
ntfsjournal.USN_REASON_EA_CHANGE
ntfsjournal.USN_REASON_FILE_CREATE
ntfsjournal.USN_REASON_FILE_DELETE
ntfsjournal.USN_REASON_HARD_LINK_CHANGE
ntfsjournal.USN_REASON_RENAME_NEW_NAME
ntfsjournal.USN_REASON_RENAME_OLD_NAME
ntfsjournal.USN_REASON_SECURITY_CHANGE

""",
    classifiers = [
        "Programming Language :: C",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Filesystems",
        ]
)
