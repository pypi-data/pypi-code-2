#!/usr/bin/env python

import os
import sys
import stat
import fnmatch
import subprocess

__all__ = ['sh', 'Makefile']

commands = {
    'mkdir': os.mkdir,
    'basename': os.path.basename,
    'exit': sys.exit,
}


class Target(object):
    def __init__(self, target=None, sources=None, sh=None):
        self.target = target
        self.sources = sources
        self.sh = sh

    def __str__(self):
        return self.target

    def __call__(self, rule):
        self.rule = rule
        return self.make

    def make(self):
        if self.is_missing() or self.is_outdated():
            self.rule(self)

    def is_missing(self):
        return not self.target or not self.sh.test('-e', self.target)

    def is_outdated(self):
        if not self.sources is None:
            for src in self.sources:
                if not self.sh.sh('-c', 'test %s -ot %s' % (self.target, src)):
                    return True
        return False;


class Makefile(object):
    targets = []

    def __init__(self, sh):
        self.sh = sh

    def __call__(self, *args, **kwargs):
        kwargs.setdefault('sh', self.sh)
        target = Target(*args, **kwargs)
        self.targets.append(target)
        return target

    def run(self, rule):
        if len(sys.argv) > 1:
            for target in self.targets:
                if target.rule.__name__ == sys.argv[1]:
                    return target.make()
        else:
            rule()


class Shell(object):
    """
    >>> sh('echo', 'test')
    0
    >>> sh.echo('test')
    0
    >>> sh.get('echo', 'test')
    'test'
    >>> sh.test('-d', '/tmp')
    True
    >>> list(sh.find(type='f', exclude=['*.pyc', './.hg*']))
    ['./README.rst', './scripting.py']

    """
    path = os.environ['PATH'].split(':')
    env = {}
    last = None
    argv = sys.argv

    def __call__(self, cmd, *args, **kwargs):
        cmdargs = self._get_cmdargs(cmd, *args, **kwargs)
        cwd = os.path.abspath(os.curdir)
        self.last = subprocess.Popen(cmdargs, cwd=cwd, env=self.env)
        return self.last.wait()

    def __getattr__(self, cmd):
        def call(*args, **kwargs):
            if cmd in commands:
                return commands[cmd](*args, **kwargs)
            else:
                return self(cmd, *args, **kwargs)
        return call

    def _get_cmd(self, cmd):
        for path in self.path:
            _cmd = os.path.join(path, cmd)
            if os.path.exists(_cmd):
                return _cmd
        return False

    def _get_cmdargs(self, cmd, *args, **kwargs):
        _cmd = self._get_cmd(cmd)

        if not _cmd:
            raise Exception('command not found: %s' % cmd)

        cmdargs = [_cmd]
        if args:
            cmdargs.extend(args)
        if kwargs:
            for i in kwargs.iteritems():
                cmdargs.extend(i)
        return [str(i) for i in cmdargs]

    def get(self, cmd, *args, **kwargs):
        cmdargs = self._get_cmdargs(cmd, *args, **kwargs)
        cwd = os.path.abspath(os.curdir)
        self.last = subprocess.Popen(cmdargs, cwd=cwd, env=self.env,
                                     stdout=subprocess.PIPE)
        self.last.wait()
        return self.last.stdout.read().strip()

    def mkdirs(self, *paths, **kwargs):
        mode = kwargs.get('mode', 0777)
        for path in paths:
            try:
                os.makedirs(path, mode)
            except OSError:
                pass

    def matches(self, f, patterns):
        for pat in patterns:
            if fnmatch.fnmatch(f, pat):
                return True
        return False

    def find(self, path='.', type=None, exclude=()):
        for root, dirs, files in os.walk(path):
            if type is None or type == 'd':
                for d in dirs:
                    if self.matches(os.path.join(root, d), exclude):
                        continue
                    yield os.path.join(root, d)
            if type is None or type == 'f':
                for f in files:
                    if self.matches(os.path.join(root, f), exclude):
                        continue
                    yield os.path.join(root, f)

    def test(self, mode, f):
        if not os.path.exists(f):
            return False

        if mode == '-e':
            return True

        modes = {
            '-b': stat.S_ISBLK,
            '-c': stat.S_ISCHR,
            '-d': stat.S_ISDIR,
            '-f': stat.S_ISREG,
            '-h': stat.S_ISLNK,
            '-L': stat.S_ISLNK,
            '-p': stat.S_ISFIFO,
            '-S': stat.S_ISSOCK,
        }
        if mode in modes:
            return modes[mode](os.stat(f)[stat.ST_MODE])

        raise Exception('test: Unknown condition: %s' % mode)

sh = Shell()
