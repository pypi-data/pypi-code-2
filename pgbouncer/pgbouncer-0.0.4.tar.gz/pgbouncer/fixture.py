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

YIELD_TIME = 0.02  # How much time to sleep in busy loops.
PROCESS_TIMEOUT = 5  # How long we wait for pgbouncer to startup and shutdown.

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
        # pgbouncer -> path to pgbouncer executable
        self.pgbouncer = 'pgbouncer'
        # dbname -> connect string
        self.databases = {}
        # username -> details
        self.users = {}
        # list of usernames that can all console queries
        self.admin_users = []
        # list of usernames that can run readonly console queries
        self.stats_users = []
        self.pool_mode = 'session'
        self.unix_socket_dir = None

    def setUp(self):
        super(PGBouncerFixture, self).setUp()
        self.host = '127.0.0.1'
        self.port = _allocate_ports()[0]
        self.configdir = self.useFixture(TempDir())
        self.auth_type = 'trust'
        self.setUpConf()
        self.start()

    def setUpConf(self):
        """Create a pgbouncer.ini file."""
        self.inipath = os.path.join(self.configdir.path, 'pgbouncer.ini')
        self.authpath = os.path.join(self.configdir.path, 'users.txt')
        self.logpath = os.path.join(self.configdir.path, 'pgbouncer.log')
        self.pidpath = os.path.join(self.configdir.path, 'pgbouncer.pid')
        with open(self.inipath, 'wt') as inifile:
            inifile.write('[databases]\n')
            for item in self.databases.items():
                inifile.write('%s = %s\n' % item)
            inifile.write('[pgbouncer]\n')
            inifile.write('pool_mode = %s\n' % (self.pool_mode,))
            inifile.write('listen_port = %s\n' % (self.port,))
            inifile.write('listen_addr = %s\n' % (self.host,))
            if self.unix_socket_dir is not None:
                inifile.write(
                    'unix_socket_dir = %s\n' % (self.unix_socket_dir,))
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
        if self.process is None:
            return
        try:
            self.process.terminate()
            # Wait for the shutdown to occur
            start = time.time()
            stop = start + PROCESS_TIMEOUT
            while self.process.poll() is None and time.time() < stop:
                time.sleep(YIELD_TIME)
        finally:
            # If its not going away, we might want to raise an error,
            # but for now it seems reliable.
            self.process = None

    def start(self):
        self.addCleanup(self.stop)

        # Add /usr/sbin if necessary to the PATH for magic just-works
        # behavior with Ubuntu.
        env = None
        if not self.pgbouncer.startswith('/'):
            path = os.environ['PATH'].split(':')
            if '/usr/sbin' not in path:
                path.append('/usr/sbin')
                env = os.environ.copy()
                env['PATH'] = ':'.join(path)

        self.process = subprocess.Popen(
            [self.pgbouncer, '-q', self.inipath], env=env,
            stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        self.process.stdin.close()

        # Wait up to 5 seconds for pgbouncer to launch start responding, or
        # raise an exception.
        now = time.time()
        stop = now + PROCESS_TIMEOUT
        while True:
            try:
                test_socket = socket.create_connection(
                    ('127.0.0.1', self.port), stop - now)
                return
            except Exception:
                now = time.time()
                if now >= stop:
                    raise
            time.sleep(YIELD_TIME)
