#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = [
    'PGBouncerFixture',
    ]

import os.path
import socket
import signal
import subprocess
import time

from fixtures import Fixture, TempDir

def _allocate_ports(n=1):
    """Allocate `n` unused ports.
    
    There is a small race condition here (between the time we allocate the
    port, and the time it actually gets used), but for the purposes for which
    this function gets used it isn't a problem in practice.
    """
    sockets = map(lambda _: socket.socket(), xrange(n))
    try:
        for s in sockets:
            s.bind(('localhost', 0))
        return map(lambda s: s.getsockname()[1], sockets)
    finally:
        for s in sockets:
            s.close()


class PGBouncerFixture(Fixture):
    """Programmatically configure and run pgbouncer.
    
    >>> Minimal usage:
    >>> bouncer = PGBouncerFixture()
    >>> bouncer.databases['mydb'] = 'host=hostname dbname=foo'
    >>> bouncer.users['user1'] = 'credentials'
    >>> with bouncer:
    ...     # Can now connect to bouncer.host port=bouncer.port user=user1
    """

    def __init__(self):
        super(PGBouncerFixture, self).__init__()
        # defaults
        # dbname -> connect string
        self.databases = {}
        # username -> details
        self.users = {}
        # list of usernames that can all console queries
        self.admin_users = []
        # list of usernames that can run readonly console queries
        self.stats_users = []
        self.pool_mode = 'session'

    def setUp(self):
        super(PGBouncerFixture, self).setUp()
        self.host = '127.0.0.1'
        self.port = _allocate_ports()[0]
        self.configdir = self.useFixture(TempDir())
        self.auth_type = 'trust'
        self.process_pid = None
        self.setUpConf()
        self.start()

    def setUpConf(self):
        """Create a pgbouncer.ini file."""
        self.inipath = os.path.join(self.configdir.path, 'pgbouncer.ini')
        self.authpath = os.path.join(self.configdir.path, 'users.txt')
        self.logpath = os.path.join(self.configdir.path, 'pgbouncer.log')
        self.pidpath = os.path.join(self.configdir.path, 'pgbouncer.pid')
        self.outputpath = os.path.join(self.configdir.path, 'output')
        with open(self.inipath, 'wt') as inifile:
            inifile.write('[databases]\n')
            for item in self.databases.items():
                inifile.write('%s = %s\n' % item)
            inifile.write('[pgbouncer]\n')
            inifile.write('pool_mode = %s\n' % (self.pool_mode,))
            inifile.write('listen_port = %s\n' % (self.port,))
            inifile.write('listen_addr = %s\n' % (self.host,))
            inifile.write('auth_type = %s\n' % (self.auth_type,))
            inifile.write('auth_file = %s\n' % (self.authpath,))
            inifile.write('logfile = %s\n' % (self.logpath,))
            inifile.write('pidfile = %s\n' % (self.pidpath,))
            adminusers = ','.join(self.admin_users)
            inifile.write('admin_users = %s\n' % (adminusers,))
            statsusers = ','.join(self.stats_users)
            inifile.write('stats_users = %s\n' % (statsusers,))
        with open(self.authpath, 'wt') as authfile:
            for user_creds in self.users.items():
                authfile.write('"%s" "%s"\n' % user_creds)

    def stop(self):
        if self.process_pid is None:
            return
        os.kill(self.process_pid, signal.SIGTERM)
        # Wait for the shutdown to occur
        start = time.time()
        stop = start + 5.0
        while time.time() < stop:
            if not os.path.isfile(self.pidpath):
                self.process_pid = None
                return
        # If its not going away, we might want to raise an error, but for now
        # it seems reliable.

    def start(self):
        self.addCleanup(self.stop)
        outputfile = open(self.outputpath, 'wt')
        self.process = subprocess.Popen(['pgbouncer', '-d', self.inipath],
            stdout=outputfile.fileno(), stderr=outputfile.fileno())
        self.process.communicate()
        # Wait up to 5 seconds for the pid file to exist
        start = time.time()
        stop = start + 5.0
        while time.time() < stop:
            if os.path.isfile(self.pidpath):
                self.process_pid = int(file(self.pidpath, 'rt').read())
                return
        raise Exception('timeout waiting for pgbouncer to create pid file')
