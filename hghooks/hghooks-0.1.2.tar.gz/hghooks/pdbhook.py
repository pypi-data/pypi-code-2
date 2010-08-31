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

import re
import os

from hghooks import skip_file, re_options


def pretxncommit(ui, repo, hooktype, node, pending, **kwargs):
    skip_text = 'no-pdb'

    ctx = repo[node]
    repo_path = pending()
    files = ctx.files()
    msg = ctx.description()

    filecontexts = list(ctx)

    # if the skip text is found in the message, skip the whole commit
    if skip_text in msg:
        return False

    pdb_catcher = re.compile(r'^[^#]*pdb\.set_trace\(\)', re_options)

    warnings = 0
    for f in files:
        if f not in filecontexts:
            continue  # this file was removed

        filename = os.path.join(repo_path, f)

        # if the skip text is found in the file, skip it
        if skip_file(filename, skip_text):
            continue

        local_warnings = len(pdb_catcher.findall(open(filename, 'r').read()))

        if local_warnings:
            print '%s: pdb found' % filename
            warnings += local_warnings

    if warnings:
        return True   # failure
    else:
        return False  # sucess
