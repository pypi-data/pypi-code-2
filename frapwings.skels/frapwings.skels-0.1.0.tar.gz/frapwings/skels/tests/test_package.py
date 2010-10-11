#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
#import unittest
from os import chdir
from nose.tools import *
from paste.script.command import run

cur_dir = os.path.abspath(os.path.dirname(__file__))
exe_dir = os.path.abspath(os.path.dirname(sys.executable))
tmp_dir = os.getenv('TEMP','/tmp')
package_name = 'package'


def paster(args):
    try:
        run(args.split(' '))
    except SystemExit:
        pass

def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)

#def read_sh(cmd):
#    _cmd = cmd
#    old = sys.stdout 
#    child_stdout_and_stderr, child_stdin = popen2.popen4(_cmd)
#    child_stdin.close()
#    return child_stdout_and_stderr.read()
#
#def sh(cmd):
#    _cmd = cmd
#    print cmd
#    # launch command 2 times to see what append and be able 
#    # to test in doc tests
#    os.system(_cmd)
#    child_stdout_and_stderr, child_stdin = popen2.popen4(_cmd)
#    child_stdin.close()
#    print child_stdout_and_stderr.read()
#
def ls(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        filenames = os.listdir(dirname)
        for filename in sorted(filenames):
            print filename
    else:
        print 'No directory named %s' % dirname

#def cd(*args):
#    dirname = os.path.join(*args)
#    os.chdir(dirname)
#
#def config(filename):
#    return os.path.join(current_dir, filename)
#
#def cat(*args):
#    filename = os.path.join(*args)
#    if os.path.isfile(filename):
#        print open(filename).read()
#    else:
#        print 'No file named %s' % filename
#
#def touch(*args, **kwargs):
#    filename = os.path.join(*args)
#    open(filename, 'w').write(kwargs.get('data',''))

def setup_func():
    package_dir = os.path.split(cur_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    chdir(tmp_dir)

def teardown_func():
    rmdir(tmp_dir, package_name)
    chdir(cur_dir)

def _diff_elements(elements1, elements2):
    return [element for element in elements2 if not element in elements1]

@with_setup(setup_func, teardown_func)
def test_package():
    paster('create -t frapwings_package %s --no-interactive' % package_name)
    dir_path = os.path.join(tmp_dir, package_name)
    assert os.path.isdir(dir_path)

    elements = ('.gitignore', 'CHANGES.txt', 'LICENSE.txt', 'README.txt',
                'MANIFEST.in', 'frapwings', 'package.egg-info', 'setup.py')
    assert len(_diff_elements(elements, os.listdir(dir_path))) == 0

    dir_path = os.path.join(dir_path, 'frapwings')
    assert os.path.isdir(dir_path)
    
    elements = ('__init__.py', '__init__.pyc', 'package')
    assert len(_diff_elements(elements, os.listdir(dir_path))) == 0

    dir_path = os.path.join(dir_path, 'package')
    assert os.path.isdir(dir_path)

    elements = ('__init__.py')
    assert len(_diff_elements(elements, os.listdir(dir_path))) == 0

