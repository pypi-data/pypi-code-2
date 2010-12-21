##
## http.py
## Login : <uli@pu.smp.net>
## Started on  Tue Apr 20 17:19:38 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""A HTTP client for ODLS indexer.
"""
import cookielib
import mimetools
import mimetypes
import os
import socket
import urllib
import urllib2
import zlib
from pysqlite2 import dbapi2 as sqlite3
from ulif.pynotify import FILE_TYPE, ADDED, MODIFIED, DELETED
from ulif.pynotify.base import FSChange
from ulif.pynotify.sqlite import FLAGS
from odls.client.logger import get_component_logger
from odls.client.util import split_path

COOKIE_JAR = cookielib.CookieJar()

class ODLSHTTPClient(object):
    """This client feeds data to an ODLS server.
    """

    def __init__(self, app):
        self.app = app
        self.logger = get_component_logger(self.app.config, 'http')
        self.logger.debug('Initializing HTTP client component')
        self.options = app.config.options
        if self.options.proxy_server is not None:
            self.logger.warn('You specified a proxy server in config.')
            self.logger.warn('Proxying is currently not supported!')
            self.logger.warn('Ignoring this option.')
        self.server_url = self.options.server_url
        # We disable that test for now, as the URL is set in default.ini
        #if self.server_url == "" or self.server_url is None:
        #    raise ValueError('No server URL specified')
        self.opener = extended_opener(
            host=self.options.server_url,
            username=self.options.http_username,
            password=self.options.http_password)
        self.hostname = socket.getfqdn()
        if self.options.nohttpout:
            return
        self.prepareDataBase()
            
    def stop(self):
        pass

    def _execute(self, func, statement, args=None):
        """Execute the SQL statement with args on cursor.
        """
        try:
            if args is not None:
                func(statement, args)
            else:
                func(statement)
        except:
            self.conn.rollback()
            raise
        finally:
            self.conn.commit()
        return

    def execute(self, cursor, statement, args=()):
        """Execute the SQL `statement` with `args` on `cursor`.

        Safe SQL execution of the given SQL `statement`. Performs a
        rollback if unsuccessful and always commits.
        """
        self._execute(cursor.execute, statement, args)
        return

    def executescript(self, cursor, script):
        """Execute the SQL script with args on cursor.
        """
        self._execute(cursor.executescript, script, None)
        return

    def prepareDataBase(self):
        """Prepare the local database.
        """
        self.conn = sqlite3.connect(self.options.dbfile)
        cur = self.conn.cursor()
        self.executescript(
            cur,
            """CREATE TABLE IF NOT EXISTS seenchanges(
                 id INTEGER PRIMARY KEY,
                 changeid INTEGER
               );
            """)
        cur.close()
        self.conn.close()
        return

    def markUnsent(self, change):
        """Mark an entry as unsent in the database.
        """
        if self.options.watch_ignore_odls_failure:
            return
        cur = self.conn.cursor()
        self.execute(
            cur,
            """REPLACE INTO seenchanges(changeid) VALUES (
                 (SELECT id FROM filechanges
                  WHERE path=?)
               )
            """,
            (change.path,)
            )
        return

    def markSent(self, change):
        """Remove entry from unsent changes tables.
        """
        cur = self.conn.cursor()
        self.execute(
            cur,
            """DELETE FROM seenchanges WHERE
                 changeid=(
                   SELECT seenchanges.changeid FROM filechanges,seenchanges
                   WHERE filechanges.id=seenchanges.changeid AND
                         filechanges.path=?)
            """,
            (change.path,)
            )
        return

    def handleResponse(self, response, change):
        """Handle server response for notifying of change.
        """
        if getattr(response, 'code', None) != 200:
            # No response at all or wrong status code...
            self.markUnsent(change)
        elif not response.read().startswith('auth OK, write OK'):
            # Valid HTTP response but server signals trouble...
            self.markUnsent(change)
        else:
            # Delete entry from DB
            self.markSent(change)
        self.opener.close()
        return
        
    def sendUnsentChanges(self):
        """Try to send changes that did not make it to the server yet.
        """
        if self.options.nohttpout:
            return
        self.conn = sqlite3.connect(self.options.dbfile)
        cur = self.conn.cursor()
        try:
            self.execute(
                cur,
                """SELECT filechanges.* FROM filechanges,seenchanges
                   WHERE filechanges.id=seenchanges.changeid
                """,
                )
        except:
            return
        for cid, path, status, ts in cur:
            change = FSChange(path, status)
            response = self.sendChange(change)
            self.handleResponse(response, change)
        self.conn.close()
        return

    def sendChanges(self, changes):
        """Send changes in ``changes`` to a server.

        This method also updates the database to remember unsuccessful
        tries enabling later retries.

        ``changes`` is expected to be some iterable on
        `ulif.pynotify.base.FSChange` objects, preferably an iterator
        over those.
        """
        if self.options.nohttpout:
            return
        self.conn = sqlite3.connect(self.options.dbfile)
        for change in changes:
            if change.filetype is not FILE_TYPE:
                # We do not send directory changes...
                continue
            response = self.sendChange(change)
            self.handleResponse(response, change)
        self.conn.close()
        return

    def sendChange(self, change):
        """Send a single change to the server.

        This method does not store results in the database.
        """

        fields, files = self.getMultipartData(change)
        content_type, body = encode_multipart_formdata(fields, files)
        headers = {'Content-Type': content_type,
                   'Content-Length': str(len(body))}
        request = urllib2.Request(self.server_url, body, headers)
        response = send_request(self.opener, request)
        if response is None:
            self.logger.warn("Couldn't connect to server. Will retry.")
        return response

    def getData(self, change):
        """Get a list of key-value pairs to submit.
        """
        size = 0
        if change.changetype is not DELETED and change.filetype is FILE_TYPE:
            size = os.path.getsize(change.path)
        status = 'unknown'
        if change.changetype is DELETED:
            status = 'missing'
        elif change.changetype is MODIFIED:
            status = 'modified'
        elif change.changetype is ADDED:
            status = 'added'
        drive, path, ext = split_path(change.path)
        result = [
            ('file_info[descr]', ''),
            ('file_info[fsize]', str(size)),
            ('file_info[status]', status),
            ('file_info[fext]', ext),
            ('file_info[share_name]', drive),
            # We do not parse files to fulltext...
            ('file_info[fulltext_error]', '1'),
            ('file_info[user_machine]', self.hostname),
            ('user[uname]', self.options.odls_username),
            ('user[pword]', self.options.odls_password),
            ]
        # Add path of file in pieces...
        for num, path_part in enumerate(path.split('/')[1:]):
            result.append(('file_info[path][%s]' % num, path_part))
        # Add ODLS vars...
        for key, value in self.options.odls_vars.items():
            result.append(('ODLS_VARS[%s][]' % key, value))
        return result

    def getMultipartData(self, change):
        """Get a tuple with fields and files to transfer.

        The first tuple element is a list of key-value-pairs, where
        the second one is a sequence of (name, filename, value)
        elements for data to be uploaded as files.
        """
        fields = self.getData(change)
        filepath = getattr(change, 'path', None)
        if filepath is None or (self.options.send_binaries is False):
            return (fields, [])
        basename = getattr(change, 'basename', filepath)
        if self.options.send_compressed is True:
            files = [('binary_compressed',
                      filepath,
                      zlib.compress(open(filepath, 'rb').read()),
                      'application/octet-stream')
                     ]
        else:
            files = [('binary',
                      filepath,
                      open(filepath, 'rb').read(),
                      None)
                     ]
        return (fields, files)

def send_request(opener, request, retry=100):
    """Send `request` deploying the `opener`.

    `retry` tells how often to repeat the procedure if something goes
    wrong.
    """
    response = None
    while response is None and retry > 0:
        try:
            response = opener.open(request)
        except urllib2.URLError, e:
            retry -= 1
    return response

    
def extended_opener(host=None, username=None, password=None, realm=None):
    """Get an urllib2 opener supporting extra features.

    Features include:

    * basic auth

    * digest auth

    * proxies

    * cookies
    
    """
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(realm, host, username, password)
    
    basic_auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    digest_auth_handler = urllib2.HTTPDigestAuthHandler(password_mgr)
    cookie_handler = urllib2.HTTPCookieProcessor(COOKIE_JAR)

    opener =  urllib2.build_opener(
        basic_auth_handler, digest_auth_handler, cookie_handler)
    return opener
    

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    
    files is a sequence of (name, filename, value, content_type)
    elements for data to be uploaded as files. If content_type is None
    we guess some.
    
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value, content_type) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, os.path.basename(filename)))
        L.append('Content-Type: %s' % get_content_type(filename, content_type))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename, content_type=None):
    """Determine MIME type of the given path.

    If a content-type is already delivered, return this.
    """
    if content_type is not None:
        return content_type
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
