# This file is part of the egoboost package which is release under the MIT
# License. You can find the full text of the license in the LICENSE file.
# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

"""
Storage for download stats.
"""

import collections
import csv
import datetime
import re
import simplejson
import StringIO
import sqlite3
import time

import stats

class DB (object):

    """
    Database wrapper object for storing/retrieving data from a SQLite db.
    """

    def __init__(self, path, create_table=True):
        self.conn = sqlite3.connect(path, 
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.path = path

        # create table if it does not exist already
        if create_table:
            cur = self.conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS downloads (
                date DATE,
                package TEXT,
                version TEXT,
                filename TEXT,
                downloads INTEGER, 
                source TEXT,
                CONSTRAINT unique_row UNIQUE (date, package, version, filename, 
                    downloads, source) ON CONFLICT IGNORE
            )''')
            self.conn.commit()

    def __del__(self):
        # close DB connection on garbage collection
        self.conn.close()

    def __repr__(self):
        return '<ego-boost DB at %s>' % self.path

    def __iter__(self):
        # collect downloads for per package per date
        cur = self.conn.cursor()
        cur.execute("SELECT date, source, package, version, filename, "
                    "downloads FROM downloads;")
        for row in cur.fetchall():
            yield row

    def __len__(self):
        return self.count()

    def add(self, package, data, source, date=None):
        """
        Adds download data for package. ``data`` is of format ::

            {
                '0.2.0': {
                    'python-amazon-product-api-0.2.0.tar.gz': 68,
                    'python-amazon-product-api-0.2.0.win32-py2.5.exe': 15,
                    'python-amazon-product-api-0.2.0.win32-py2.5.msi': 17,
                    'python-amazon-product-api-0.2.0.win32-py2.6.exe': 17,
                    'python-amazon-product-api-0.2.0.win32-py2.6.msi': 19},
                '0.2.1': {
                    'python-amazon-product-api-0.2.1.tar.gz': 130},
                '0.2.2': {
                    'python-amazon-product-api-0.2.2.tar.gz': 101,
                    'python-amazon-product-api-0.2.2.win32.exe': 29},
                '0.2.3': {'python-amazon-product-api-0.2.3.tar.gz': 90,
                    'python-amazon-product-api-0.2.3.win32-py2.5.exe': 7}
            }
        
        which is, incidentally, the very same format that comes out of the 
        ``get_*_downloads`` functions.
        """
        if date is None:
            date = datetime.date.today()

        def build_rows():
            "Prepares data for executemany()."
            for version, files in data.items():
                # ignore meta data
                if type(files) != dict:
                    continue
                for filename, count in files.items():
                    yield {
                        'date' : date, 
                        'version' : version, 
                        'package' : package, 
                        'version' : version, 
                        'filename' : filename, 
                        'downloads' : count, 
                        'source' : source
                    }
            
        cur = self.conn.cursor()
        cur.executemany('''INSERT INTO downloads (
            date, package, version, filename, downloads, source) VALUES (
            :date, :package, :version, :filename, :downloads, :source)''',
            build_rows())
        self.conn.commit()

    def date_range(self):
        """
        Returns first and last date for which data has been stored.
        """
        cur = self.conn.cursor()
        cur.execute('''SELECT MIN(date) as "first [date]",
            MAX(date) as "last [date]" FROM downloads;''')
        return cur.fetchone()

    def count(self):
        """
        Returns total row count.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM downloads;')
        return cur.fetchone()[0]

    def get_packages(self):
        """
        Gets all packages.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT package FROM downloads;')
        return [pkg[0] for pkg in cur.fetchall()]

    def get_versions(self, pkg):
        """
        Gets all versions for a package.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT version FROM downloads '
                    'WHERE package = ?;', (pkg, ))
        return [ver[0] for ver in cur.fetchall()]

    def get_files(self, pkg, ver):
        """
        Gets all sources for a version of a package.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT filename FROM downloads '
                    'WHERE package = ? and version = ?;', (pkg, ver))
        return [src[0] for src in cur.fetchall()]

    def tocsv(self, package=None, version=None, nan=0, total=False):
        """
        Returns download statistics as CSV data.

        If no package or version is specified, the total downloads per package
        per day is returned. ::

            >>> db = DB('~/.egoboost/downloads.db')
            >>> db.tocsv()
            "date","python-amazon-product-api","python-weewar"
            "2010-05-04",7834,22
            ...
            "2010-05-13",7886,2792
            "2010-05-14",7897,2792

        If a package is given, all downloads per *version* per day are
        displayed. By additionally passing a version string, all downloads per
        *file* per day are given. Note that version alone (without package) 
        will be ignored.

        Parameter ``nan`` specifies how empty values are going to show up in
        the CSV data. ::

            >>> db.tocsv('python-weewar', '0.3', nan='null')
            "date","python-weewar-0.3-dev.tar.gz","python-weewar-0.3.tar.gz","python-weewar_0.3-ubuntu1_all.deb"
            "2009-10-05",0,0,"null"
            "2009-10-06",5,4,"null"
            "2009-10-07",5,4,"null"
            "2009-10-08",5,4,"null"
            "2009-10-09",5,4,"null"
            "2009-10-10",5,4,"null"
        """
        # abort processing for no data
        if len(self)==0:
            return ''

        # collect download information
        cur = self.conn.cursor()
        if package and version:
            if package not in self.get_packages():
                raise ValueError('Unknown package %r!' % package)
            if version not in self.get_versions(package):
                raise ValueError('Unknown version %r!' % version)
            cur.execute("""SELECT date, filename, SUM(downloads) FROM downloads
            WHERE package = ? and version = ?
            GROUP BY date, filename;""", (package, version))
            headers = self.get_files(package, version)
        elif package:
            if package not in self.get_packages():
                raise ValueError('Unknown package %r!' % package)
            cur.execute("""SELECT date, version, SUM(downloads) FROM downloads
            WHERE package = ?
            GROUP BY date, package, version;""", (package, ))
            headers = self.get_versions(package)
        else:
            cur.execute("""SELECT date, package, SUM(downloads) FROM downloads
            GROUP BY date, package;""")
            headers = self.get_packages()

        # write CSV headers
        buffer = StringIO.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['date'] + headers)

        # read data from db
        data = collections.defaultdict(lambda: collections.defaultdict(lambda: nan))
        for date, col, count in cur.fetchall():
            data[col][date] = count

        # calculate increments
        if not total:
            for col, ts in data.iteritems():
                interpolated = stats.linear_interpolation(ts)
                first, prev = interpolated.next() 
                for date, count in interpolated:
                    data[col][date] = int(round(count-prev))
                    prev = count

        # write data to CSV
        date_range = reduce(lambda a,b: a+b,
                            [data[col].keys() for col in data.keys()])
        current, last = min(date_range), max(date_range)
        while current <= last:
            writer.writerow([current] + [data[col][current] for col in headers])
            current += datetime.timedelta(days=+1)
        buffer.flush()
        return buffer.getvalue()


def read_json(fp):
    """
    Loads download data from JSON file. Newer versions store meta data as well::

        {u'0.2.3': {...}, 
        '_package': 'python-amazon-product-api', 
        '_source': 'pypi', 
        '_date': datetime.date(2010, 6, 10)}

    Older versions store this data in the file name itself (eg. 
    ``pypi-20100610-python-amazon-product-api.json``). A ``ValueError`` is 
    raised if this data cannot be extracted.
    """
    blocks = simplejson.load(fp)
    if type(blocks) == dict:
        blocks = [blocks]
    # Old versions have meta data in file name. If no meta data can be found
    # (ie. _source, _date, _package) try to extract it from the file name.
    for data in blocks:
        if not '_date' in data:
            filename = fp.name
            m = re.search('(?P<_source>\w+)-(?P<_date>\d{8})-'
                        '(?P<_package>[\w-]+)', filename)
            if not m:
                raise ValueError('No meta data found!')
            data.update(m.groupdict())
            data['_date'] = datetime.date(
                *time.strptime(data['_date'], '%Y%m%d')[:3])
    return data


if __name__ == '__main__':

    # load/create database
    db = DB('/home/basti/.ego-boost/downloads.db')
    first, last = db.date_range()
    print '%i rows from %s to %s.' % (db.count(), first, last)

    # show data
    print db.tocsv('python-weewar')
    print db.tocsv('python-amazon-product-api', '0.2.4', 'null')

#    # fetch data and store in db
#    from utils import get_downloads
#    data = get_downloads('http://bitbucket.org/basti/python-amazon-product-api/')
#    db.add('python-amazon-product-api', data, 'bitbucket')

#    # import old data from JSON files
#    import os, os.path
#    for filename in os.listdir('data'):
#        print 'Loading %s...' % filename
#        try:
#            data = read_json(open(os.path.join('data', filename)))
#            db.add(data['_package'], data, data['_source'], data['_date'])
#        except ValueError, e:
#            print 'ERROR:', e

