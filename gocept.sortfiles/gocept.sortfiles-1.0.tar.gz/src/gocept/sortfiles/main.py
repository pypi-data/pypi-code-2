# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import os
import sys


def sort_files():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: %s directory' % sys.argv[0])
    _sort_files(sys.argv[1])


def _sort_files(directory):
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        if not os.path.isfile(file):
            continue
        ctime = datetime.datetime.fromtimestamp(os.stat(file).st_ctime)
        target = os.path.join(
            directory,
            str(ctime.year),
            '%02d' % ctime.month,
            '%02d' % ctime.day)
        if not os.path.exists(target):
            os.makedirs(target)
        os.rename(file, os.path.join(target, filename))
