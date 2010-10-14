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

import os.path
import re
import shutil
import sys
import tempfile

import pep8
from pyflakes.scripts import pyflakes

version = "0.2.0"

re_options = re.IGNORECASE | re.MULTILINE | re.DOTALL
skip_pattern = re.compile('# hghooks: (.*)', re_options)


class CheckerManager(object):

    def __init__(self, ui, repo, node, skip_text):
        self.ui = ui
        self.repo = repo
        self.node = node
        self.skip_text = skip_text

    def skip_file(self, filename, filedata):
        if not filename.endswith('.py'):
            return True

        for match in skip_pattern.findall(filedata):
            if self.skip_text in match:
                return True

        return False

    def check(self, checker):
        warnings = 0
        current_rev = self.repo[self.node].rev()
        total_revs = len(self.repo.changelog)
        while current_rev < total_revs:
            current_rev += 1
            rev_warnings = 0
            directory = tempfile.mkdtemp(suffix='-r%d' % (current_rev - 1),
                                         prefix='hghooks')

            self.ui.debug("Checking revision %d\n" % current_rev)
            ctx = self.repo[current_rev - 1]
            if self.skip_text in ctx.description():
                continue

            files_to_check = {}
            existing_files = tuple(ctx)
            for filename in ctx.files():

                if filename not in existing_files:
                    continue  # the file was removed in this changeset

                filectx = ctx.filectx(filename)
                filedata = filectx.data()

                if self.skip_file(filename, filedata):
                    continue

                full_path = os.path.join(directory, filename)
                files_to_check[full_path] = filedata

            if files_to_check:
                rev_warnings += checker(files_to_check)

            if rev_warnings:
                self.ui.warn('%d warnings found in revision %d\n' %
                             (rev_warnings, current_rev - 1))
            else:
                self.ui.debug('No warnings in revision %d. Good job!\n' %
                              (current_rev - 1))
            warnings += rev_warnings
            shutil.rmtree(directory)

        if warnings:
            return True   # failure
        else:
            return False  # sucess


def pep8_checker(files_to_check):
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


def pdb_checker(files_to_check):

    def check_one_file(data, filename):
        warnings = len(pdb_catcher.findall(open(filename, 'r').read()))
        if warnings > 0:
            print '%s: pdb found' % filename
        return warnings

    return sum([check_one_file(data, filename)
                for filename, data in files_to_check.items()])


def pdbhook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pdb')
    return checker_manager.check(pdb_checker)


def pyflakes_checker(files_to_check):
    return sum([pyflakes.check(data, filename)
                for filename, data in files_to_check.items()])


def pyflakeshook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pyflakes')
    return checker_manager.check(pyflakes_checker)
