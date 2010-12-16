## Copyright (c) 2010 dotCloud Inc.
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

import os
import time
import subprocess
from contextlib import contextmanager

from utils import die, info, parse_url


class Remote(object):

    def set_url(self, url):
        parts = parse_url(url)
        (self._user, self._host, self._port) = (parts['user'] or 'dotcloud', parts['host'], parts['port'] or '22')
        self._url = url
        self._ssh_master = None
        self._ssh_sock = '/tmp/dotcloud-{0}.sock'.format(time.time())
        self._ssh_common_args = (
                '-q', '-p', self._port,
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-S', self._ssh_sock
        )

    def __del__(self):
        if self._ssh_master is not None and self._ssh_master.poll() is None:
            self._ssh_master.terminate()

    def _spawn_ssh_master(self):
        if self._ssh_master is None or self._ssh_master.poll() is not None:
            self._ssh_master = subprocess.Popen(
                (
                    'ssh', '-q',
                    '-l', self._user, self._host,
                    '-o', 'ServerAliveInterval=10',
                    '-M'
                ) + self._ssh_common_args + ( 'echo ok ; cat', ),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._ssh_master.stdout.read(3) == 'ok\n' or die("SSH connection failed on '{0}'".format(self._url))

    def _escape(self, s):
        for c in ('`', '$', '"'):
            s = s.replace(c, '\\' + c)
        return s

    def _ssh(self, cmd, tty=True, **kwargs):
        self._spawn_ssh_master()
        p_args = (
                'ssh', '-t' if tty else '-T',
                '-l', self._user, self._host,
                ) + self._ssh_common_args + (
                        'bash -l -c "{0}"'.format(self._escape(cmd))
                        ,)
        return subprocess.Popen(p_args, **kwargs)

    def _scp(self, src, dest):
        self._spawn_ssh_master()
        scp = (
                'scp', '-q', '-P', self._port, '-r',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ControlPath={0}'.format(self._ssh_sock),
                src, dest
        )
        return subprocess.call(scp, close_fds=True)

    def push(self, src, dest='.'):
        info('# push {0} {1}'.format(src, dest))
        return self._scp(src, '{user}@{host}:{dest}'.format(user=self._user, host=self._host, dest=dest))

    def pull(self, src, dest='.'):
        info('# pull {0} {1}'.format(src, dest))
        return self._scp('{user}@{host}:{src}'.format(user=self._user, host=self._host, src=src), dest)

    def run(self, *args):
        cmd = ' '.join(args)
        info('# {0}'.format(cmd))
        return self._ssh(cmd).wait()

    def run_script(self, script):
        proc = self._ssh('/bin/bash', tty=False, stdin=subprocess.PIPE)
        proc.stdin.write(script)
        proc.communicate()

    def rsync(self, local_dir, remote_dir, exclude=()):
        info('# rsync {0} {1}'.format(local_dir, remote_dir))
        if not hasattr(exclude, '__iter__'):
            exclude = (exclude,)
        self._spawn_ssh_master()
        rsync = (
                    'rsync', '-lpthrvz', '--delete', '--safe-links',
                ) + tuple('--exclude={0}'.format(e) for e in exclude) + (
                    '-e', 'ssh {0}'.format(' '.join(self._ssh_common_args)),
                    '{0}/'.format(local_dir),
                    '{user}@{host}:{dest}/'.format(user=self._user, host=self._host, dest=remote_dir)
                )
        return subprocess.call(rsync, close_fds=True)
