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

import utils


class Remote(object):

    def set_url(self, url):
        parts = utils.parse_url(url)
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

    def die(self, progname):
        utils.die('Error: "{0}" failed to be executed. Please make sure it is properly installed.'.format(progname))

    def _spawn_ssh_master(self):
        if self._ssh_master and self._ssh_master.poll() is None:
            return
        try:
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
            if self._ssh_master.stdout.read(3) != 'ok\n':
                utils.die("SSH connection failed on '{0}'".format(self._url))
        except OSError:
            self.die('ssh')

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
        utils.info('# push {0} {1}'.format(src, dest))
        return self._scp(src, '{user}@{host}:{dest}'.format(user=self._user, host=self._host, dest=dest))

    def pull(self, src, dest='.'):
        utils.info('# pull {0} {1}'.format(src, dest))
        return self._scp('{user}@{host}:{src}'.format(user=self._user, host=self._host, src=src), dest)

    def run(self, *args):
        cmd = ' '.join(args)
        utils.info('# {0}'.format(cmd))
        return self._ssh(cmd).wait()

    def run_script(self, script):
        proc = self._ssh('/bin/bash', tty=False, stdin=subprocess.PIPE)
        proc.stdin.write(script)
        proc.communicate()

    def rsync(self, local_dir, destination, exclude=()):
        utils.info('# rsync')
        url = utils.parse_url(destination)
        if not hasattr(exclude, '__iter__'):
            exclude = (exclude,)
        ssh_command = 'ssh -q -p {0}'.format(url['port'])
        ssh_command += ' -o UserKnownHostsFile=/dev/null'
        ssh_command += ' -o StrictHostKeyChecking=no'
        ssh_command += ' -o ServerAliveInterval=10'
        if not local_dir.endswith('/'):
            local_dir += '/'
        rsync = (
                    'rsync', '-lpthrvz', '--delete', '--safe-links',
                ) + tuple('--exclude={0}'.format(e) for e in exclude) + (
                    '-e', ssh_command, local_dir,
                    '{user}@{host}:{dest}/'.format(user=url['user'], host=url['host'], dest=url['path'])
                )
        try:
            return subprocess.call(rsync, close_fds=True)
        except OSError:
            self.die('rsync')

    def hg(self, local_dir, destination, branch=None):
        utils.info('# hg')
        if not branch:
            branch = 'default'
        with utils.cd(local_dir):
            try:
                return subprocess.call(('hg', 'push', '-f', destination, '-b', branch), close_fds=True)
            except OSError:
                self.die('hg')

    def git(self, local_dir, destination, branch=None):
        utils.info('# git')
        if not branch:
            branch = 'master'
        with utils.cd(local_dir):
            try:
                return subprocess.call(('git', 'push', '-f', destination, branch), close_fds=True)
            except OSError:
                self.die('git')

    def upload(self, local_dir, destination):
        utils.info('# upload {0} {1}'.format(local_dir, destination))
        if os.path.isdir(os.path.join(local_dir, '.hg')):
            return self.hg(local_dir, destination)
        if os.path.isdir(os.path.join(local_dir, '.git')):
            return self.git(local_dir, destination)
        return self.rsync(local_dir, destination)
