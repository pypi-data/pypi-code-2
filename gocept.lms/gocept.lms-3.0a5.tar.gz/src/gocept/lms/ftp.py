# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Checker implementation for the FTP."""

import logging
import urllib
import ftplib
import socket
import grok

import gocept.lms.handler

from gocept.lms.interfaces import STATE_OK, STATE_UNAVAILABLE, STATE_TEMPORARY

log = logging.getLogger(__name__)


class FTP(gocept.lms.handler.AbstractURLHandler,
          grok.GlobalUtility):

    grok.name('ftp')

    def check(self, url):
        protocol, url = urllib.splittype(url)
        host, path = urllib.splithost(url)
        username, host = urllib.splituser(host)
        host, port = urllib.splitport(host)

        if username:
            username, password = urllib.splitpasswd(username)
        else:
            username = 'anonymous'
            password = 'mail+lms@gocept.com'

        try:
            connection = ftplib.FTP(host, username, password)
        except socket.gaierror, e:
            return STATE_UNAVAILABLE, e.args[1]
        except Exception, e:
            return STATE_UNAVAILABLE, str(e)

        # Try to find out whether this is a file or a directory
        try:
            connection.set_pasv(True)
            lst = connection.nlst(path)
        except Exception, e:
            connection.quit()
            return STATE_UNAVAILABLE, str(e)

        if lst == [path]:
            # `path` referes to a file. Try to download a bit.
            try:
                connection.retrbinary('RETR %s' % path, accept_data)
            except FTPSuccess:
                connection.close()
                return STATE_OK, 'Transfer successfully started.'
            except Exception, e:
                connection.quit()
                return STATE_UNAVAILABLE, str(e)
        else:
            # `path` refers to a directory and we were able to list it.
            connection.quit()
            return STATE_OK, 'Directory successfully listed'


class FTPSuccess(Exception):
    """Signal that FTP data transfer started."""

def accept_data(data):
    raise FTPSuccess()
