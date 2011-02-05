"""pyverify.verify.py

Verify Python distributions installed via distutils2.
"""
from __future__ import print_function
import os
import sys
import hashlib

from distutils2._backport.pkgutil import Distribution
from distutils2._backport.pkgutil import get_distribution


STATUS_CODES = {
    0: {'display': 'ok', 'description': 'file ok'},
    1: {'display': 'md5', 'description': 'md5 mismatch'},
    2: {'display': '?', 'description': 'missing'},
    3: {'display': 'ok', 'description': 'dist ok'},
    4: {'display': 'md5', 'description': 'installed file(s) md5 mismatch'},
    5: {'display': '!', 'description': 'distribution not installed'},
    6: {'display': '?', 'description': 'cannot read dist-info'}}


class VerificationException(Exception):
    """Base exception for verification scripts"""


def verify_dists(dists=None, paths=None):
    """Verify all distributions provided in dists.

    Return a generator of verified distributions tuples
    """
    if paths is None:
        paths = sys.path

    for dist in dists:
        if not isinstance(dist, Distribution):
            dist = get_distribution(dist, paths=paths)

        name = dist
        details = {}

        if dist is None:
            details['verified_files'] = None
            details['status'] = 5
        else:
            name = dist.name
            if os.path.isfile(os.path.join(
                dist.path, 'RECORD')):
                installed_files = dist.get_installed_files()
                verified_files = [f for f in verify_installed_files(
                                                 installed_files)]
                details['verified_files'] = verified_files
                if all([_status_ok(record) for record in verified_files]):
                    details['status'] = 3
                else:
                    details['status'] = 4
            else:
                details['verified_files'] = None
                details['status'] = 6
        yield (name, details)


def _status_ok(record):
    """Check the record status field (position 3), if 0
    the file md5sum match the installation metadata.
    """
    if record[3] == 0:
        return True
    else:
        return False


def _print_report(verified_dists):
    """Print verification report.
    """
    for name, details in verified_dists:
        status = details['status']
        desc = STATUS_CODES[status]['description']
        print("{}: {}".format(name, desc))

        verified_files = details['verified_files']
        if verified_files:
            for record in verified_files:
                status = record[3]
                display = STATUS_CODES[status]['display']
                filename = record[0]
                print("  {:4}{}".format(display, filename))


def verify_installed_files(installed_files):
    """Verify a distributions installed files.

    Return a generator of verified files.

    :param installed_files: as returned by get_installed_files()

    The process follow these steps:

        1. compare current md5sum with the one from installed_files
        2. set the file status. See STATUS_CODES for details.
    """
    for installed_file in installed_files:
        md5 = installed_file[1]
        if not md5:
            md5 = ''
        _file = installed_file[0]
        cur_md5, size, status = '', '', 0
        if md5:
            if os.path.isfile(_file):
                size = os.path.getsize(_file)
                _md5 = hashlib.new('md5')
                _md5.update(open(_file, 'r').read())
                cur_md5 = _md5.hexdigest()
                if md5 == cur_md5:
                    # The md5sum matches the metadata
                    status = 0
                else:
                    # oops we have a md5sum mismatch
                    status = 1
            else:
                # The file was listed in the metadata files but
                # does not exist on disk.
                status = 2

        yield(_file, cur_md5, size, status)


def run(dists, paths):
    """
    Verify the Python distributions.
    """
    _print_report(verify_dists(dists, paths))
