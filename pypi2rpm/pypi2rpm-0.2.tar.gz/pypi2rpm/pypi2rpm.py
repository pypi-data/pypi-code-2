#!/usr/bin/env python
import os
import sys
import tempfile
import tarfile
import shutil
import subprocess
from ConfigParser import ConfigParser

from distutils2.index.simple import Crawler


def _is_d2(location=os.curdir):
    """Returns True if the project is a Distutils2 Project"""
    setup_cfg = os.path.join(location, 'setup.cfg')
    if not os.path.exists(setup_cfg):
        return False
    f = open(setup_cfg)
    try:
        return '[metadata]' in f.read()
    finally:
        f.close()


def get_last_release(project_name):
    if os.path.exists(project_name):
        return project_name
    c = Crawler()
    project = c.get_releases(project_name)
    last_release = project[0]
    return last_release.download()


def _d1_sdist2rpm():
    # grab the name and create a normalized one
    popen = subprocess.Popen('%s setup.py --name' % sys.executable,
                                stdout=subprocess.PIPE, shell=True)
    name = [line for line in popen.stdout.read().split('\n') if line != '']
    name = name[-1].strip().lower()
    major, minor = sys.version_info[0], sys.version_info[1]

    # getting the python version
    if not name.startswith('python'):
        name = 'python%d%d-%s' % (major, minor, name)

    # run the bdist_rpm2 command
    cmd = '--command-packages=pypi2rpm.command bdist_rpm2 --fix-python'
    res = subprocess.call('%s setup.py %s --name=%s' % \
            (sys.executable, cmd, name), shell=True)
    if res != 0:
        print('Could not create RPM')
        sys.exit(0)


def _d2_sdist2rpm():
    setup_cfg = ConfigParser()
    setup_cfg.read('setup.cfg')
    name = setup_cfg.get('metadata', 'name')
    name = name.strip().lower()
    if not name.startswith('python-'):
        name = 'python-%s' % name

    # run the bdist_rpm2 command
    os.system('%s -m distutils2.run bdist_rpm2 --fix-python --name=%s' % \
            (sys.executable, name))


def sdist2rpm(sdist):
    """Creates a RPM distro out of a Python project."""
    old_dir = os.getcwd()

    if os.path.isfile(sdist):
        archive = tarfile.open(sdist)
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)
        archive.extractall(tempdir)
        sdist = os.listdir(os.curdir)[0]
    else:
        tempdir = None

    os.chdir(sdist)
    try:
        if not _is_d2():
            _d1_sdist2rpm()
        else:
            _d2_sdist2rpm()

        for file_ in os.listdir('dist'):
            if file_.endswith('.noarch.rpm'):
                target = os.path.join(old_dir, file_)
                shutil.copyfile(os.path.join('dist', file_), target)
                return target
    finally:
        os.chdir(old_dir)
        if tempdir is not None and os.path.exists(tempdir):
            shutil.rmtree(tempdir)


def main(project):
    res = sdist2rpm(get_last_release(project))
    if res is None:
        print 'Failed.'
        return 1
    print '%s written' % res
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: pypi2rpm [project name at pypi or path]'
        sys.exit(1)

    sys.exit(main(sys.argv[1]))
