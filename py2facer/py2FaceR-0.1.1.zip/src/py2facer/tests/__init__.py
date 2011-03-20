license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import logging
import os
import glob

__all__ = ['flickr', 'image', 'picasa']

BASEPATH = os.path.dirname(__file__)

TESTFILES = {'contacts' : '%s/testdata/contacts.xml' % BASEPATH,
             'ini' : '%s/testdata/.picasa.ini' % BASEPATH,
             'img' : '%s/testdata/test.jpg' % BASEPATH}
DB_COUNTER = 0
TESTDB = '%s/test%%s.db' % BASEPATH
TESTDBURL = 'sqlite:///%s' % TESTDB

def delOldDb():
    try:
        olddbfiles = glob.glob(TESTDB % '*')
        for olddb in olddbfiles:
            os.remove(olddb)
    except (IOError, WindowsError):
        # Unable to unlink this one, try again next round
        pass

