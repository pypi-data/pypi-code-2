# Copyright (c) 2010 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys

import pep8
from pyflakes.scripts import pyflakes

from hghooks import CheckerManager, re_options


def pep8_checker(files_to_check, msg):
    for filename, data in files_to_check.items():
        parentdir = os.path.dirname(filename)
        if not os.path.exists(parentdir):
            os.makedirs(parentdir)
        open(filename, 'w').write(data)

    # monkey patch sys.argv options so we can call pep8
    old_args = sys.argv

    sys.argv = ['pep8'] + files_to_check.keys()
    options, args = pep8.process_options()
    sys.argv = old_args
    for path in args:
        pep8.input_file(path)

    return pep8.get_count()


def pep8hook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pep8')
    return checker_manager.check(pep8_checker)


pdb_catcher = re.compile(r'^[^#]*pdb\.set_trace\(\)', re_options)


def pdb_checker(files_to_check, msg):

    def check_one_file(data, filename):
        warnings = len(pdb_catcher.findall(data))
        if warnings > 0:
            print '%s: pdb found' % filename
        return warnings

    return sum([check_one_file(data, filename)
                for filename, data in files_to_check.items()])


def pdbhook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pdb')
    return checker_manager.check(pdb_checker)


def pyflakes_checker(files_to_check, msg):
    return sum([pyflakes.check(data, filename)
                for filename, data in files_to_check.items()])


def pyflakeshook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pyflakes')
    return checker_manager.check(pyflakes_checker)
