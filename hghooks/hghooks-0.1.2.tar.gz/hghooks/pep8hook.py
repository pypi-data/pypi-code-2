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
import sys

import pep8

from hghooks import skip_file


def pretxncommit(ui, repo, hooktype, node, pending, **kwargs):
    skip_text = 'no-pep8'
    ctx = repo[node]
    repo_path = pending()
    files = ctx.files()
    msg = ctx.description()

    filecontexts = list(ctx)

    # if the skip text is found in the message, skip the whole commit
    if skip_text in msg:
        return False

    args = []
    for f in files:
        if f not in filecontexts:
            continue  # this file was removed

        filename = os.path.join(repo_path, f)
        if not skip_file(filename, skip_text):
            args.append(filename)

    if not args:
        return False

    # monkey patch sys.argv options so we can call pep8
    old_args = sys.argv

    sys.argv = ['pep8'] + args
    options, args = pep8.process_options()
    sys.argv = old_args
    for path in args:
        pep8.input_file(path)

    count = pep8.get_count()
    if count:
        return True   # failure
    else:
        return False  # sucess
