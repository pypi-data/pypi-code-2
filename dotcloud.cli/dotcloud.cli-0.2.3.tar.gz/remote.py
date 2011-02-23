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

    def __init__(self):
        self._verbose = True

    def __del__(self):
        if self._ssh_master is not None and self._ssh_master.poll() is None:
            self._ssh_master.terminate()

    def set_url(self, url):
        parts = utils.parse_url(url)
        (self._user, self._host, self._port) = (parts['user'] or 'dotcloud', parts['host'], parts['port'] or '22')
        self._url = url
        self._ssh_master = None
        self._ssh_sock = '/tmp/dotcloud-{0}.sock'.format(time.time())
        self._ssh_options = (
                'ssh',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'PasswordAuthentication=no',
                '-o', 'ServerAliveInterval=10'
                )

    def set_verbose(self, flag):
        self._verbose = flag

    def info(self, *args):
        if not self._verbose:
            return
        utils.info(*args)

    def die(self, progname):
        utils.die('Error: "{0}" failed to be executed. Please make sure it is properly installed.'.format(progname))

    def warning_ssh(self):
        utils.warning('Warning: Please make sure that your SSH key is configured correctly:')
        utils.warning('http://docs.dotcloud.com/static/tutorials/firststeps/#create-and-setup-your-account')
        utils.warning('Also please check that your are allowed to make an SSH connection to a custom port.')

    def _spawn_ssh_master(self):
        if self._ssh_master and self._ssh_master.poll() is None:
            return
        try:
            self._ssh_master = subprocess.Popen(
                    self._ssh_options + (
                        '-p', self._port,
                        '-l', self._user,
                        '-S', self._ssh_sock,
                        '-M',
                        self._host, 'echo ok ; cat'
                        ),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
            )
            if self._ssh_master.stdout.read(3) != 'ok\n':
                ret = self._ssh_master.poll()
                if ret is not None and ret != 0:
                    self.warning_ssh()
                utils.die('SSH connection failed on "{0}"'.format(self._url))
        except OSError:
            self.die('ssh')

    def _escape(self, s):
        for c in ('`', '$', '"'):
            s = s.replace(c, '\\' + c)
        return s

    def _ssh(self, cmd, tty=True, **kwargs):
        self._spawn_ssh_master()
        p_args = self._ssh_options + (
                '-t' if tty else '-T',
                '-l', self._user,
                '-p', self._port,
                '-S', self._ssh_sock,
                self._host,
                'bash -l -c "{0}"'.format(self._escape(cmd))
                )
        return subprocess.Popen(p_args, **kwargs)

    def _scp(self, src, dest):
        self._spawn_ssh_master()
        scp = (
                'scp', '-P', self._port, '-r',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ControlPath={0}'.format(self._ssh_sock),
                src, dest
        )
        return subprocess.call(scp, close_fds=True)

    def push(self, src, dest='.'):
        self.info('# push {0} {1}'.format(src, dest))
        return self._scp(src, '{user}@{host}:{dest}'.format(user=self._user, host=self._host, dest=dest))

    def pull(self, src, dest='.'):
        self.info('# pull {0} {1}'.format(src, dest))
        return self._scp('{user}@{host}:{src}'.format(user=self._user, host=self._host, src=src), dest)

    def run(self, *args):
        cmd = ' '.join(args)
        self.info('# {0}'.format(cmd))
        return self._ssh(cmd).wait()

    def run_script(self, script):
        proc = self._ssh('/bin/bash', tty=False, stdin=subprocess.PIPE)
        proc.stdin.write(script)
        proc.communicate()

    def rsync(self, local_dir, destination, args):
        self.info('# rsync')
        excludes = args.get('excludes')
        url = utils.parse_url(destination)
        ssh = ' '.join(self._ssh_options)
        ssh += ' -p {0}'.format(url['port'])
        if not local_dir.endswith('/'):
            local_dir += '/'
        rsync = (
                    'rsync', '-lpthrvz', '--delete', '--safe-links',
                ) + tuple('--exclude={0}'.format(e) for e in excludes) + (
                    '-e', ssh, local_dir,
                    '{user}@{host}:{dest}/'.format(user=url['user'], host=url['host'], dest=url['path'])
                )
        try:
            ret = subprocess.call(rsync, close_fds=True)
            if ret != 0:
                self.warning_ssh()
            return ret
        except OSError:
            self.die('rsync')

    def hg(self, local_dir, destination, args):
        self.info('# hg')
        branch = args.get('branch')
        with utils.cd(local_dir):
            try:
                ssh = ' '.join(self._ssh_options)
                args = ('hg', 'push', '--ssh', ssh, '-f', destination)
                if branch:
                    args += ('-b', branch)
                ret = subprocess.call(args, close_fds=True)
                if ret != 0:
                    self.warning_ssh()
                return ret
            except OSError:
                self.die('hg')

    def git(self, local_dir, destination, args):
        self.info('# git')
        branch = args.get('branch')
        if not branch:
            branch = 'master'
        with utils.cd(local_dir):
            try:
                os.environ['GIT_SSH'] = '__dotcloud_git_ssh'
                ret = subprocess.call(('git', 'push', '-f', destination, branch), close_fds=True)
                if ret != 0:
                    self.warning_ssh()
                return ret
            except OSError:
                self.die('git')

    def upload(self, local_dir, destination, args):
        self.info('# upload {0} {1}'.format(local_dir, destination))
        if os.path.isdir(os.path.join(local_dir, '.hg')):
            return self.hg(local_dir, destination, args.get('hg', {}))
        if os.path.isdir(os.path.join(local_dir, '.git')):
            return self.git(local_dir, destination, args.get('git', {}))
        return self.rsync(local_dir, destination, args.get('rsync', {}))
