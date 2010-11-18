#!/usr/bin/env python
import os
import sys
import tempfile
import tarfile
import shutil
import subprocess
import argparse
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


def _d1_sdist2rpm(dist_dir):
    # grab the name and create a normalized one
    popen = subprocess.Popen('%s setup.py --name' % sys.executable,
                                stdout=subprocess.PIPE, shell=True)
    name = [line for line in popen.stdout.read().split('\n') if line != '']
    name = name[-1].strip().lower()
    major, minor = sys.version_info[0], sys.version_info[1]

    # getting the python version
    python = 'python%d%d' % (major, minor)

    if not name.startswith('python'):
        name = '%s-%s' % (python, name)

    # run the bdist_rpm2 command
    cmd = ('--command-packages=pypi2rpm.command bdist_rpm2 '
           '--binary-only')
    if dist_dir is not None:
        cmd += ' --dist-dir=%s' % dist_dir

    call = '%s setup.py %s --name=%s --python=%s' % \
            (sys.executable, cmd, name, python)
    print(call)
    res = subprocess.call(call, shell=True)
    if res != 0:
        print('Could not create RPM')
        sys.exit(0)


def _d2_sdist2rpm(dist_dir):
    setup_cfg = ConfigParser()
    setup_cfg.read('setup.cfg')
    name = setup_cfg.get('metadata', 'name')
    name = name.strip().lower()
    if not name.startswith('python-'):
        name = 'python-%s' % name

    cmd = '-m distutils2.run bdist_rpm2 --binary-only'
    if dist_dir is not None:
        cmd += ' --dist-dir=%s' % dist_dir
    # run the bdist_rpm2 command
    os.system('%s %s --name=%s' % (sys.executable, cmd, name))


def sdist2rpm(sdist, dist_dir=None):
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
            _d1_sdist2rpm(dist_dir)
        else:
            _d2_sdist2rpm(dist_dir)

        if dist_dir is None:
            dist_dir = 'dist'
        for file_ in os.listdir(dist_dir):
            if file_.endswith('.noarch.rpm'):
                target = os.path.join(old_dir, file_)
                shutil.copyfile(os.path.join(dist_dir, file_), target)
                return target
    finally:
        os.chdir(old_dir)
        if tempdir is not None and os.path.exists(tempdir):
            shutil.rmtree(tempdir)


def main(project, dist_dir):
    res = sdist2rpm(get_last_release(project), dist_dir)
    if res is None:
        print 'Failed.'
        return 1
    print '%s written' % res
    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dist-dir', type=str, default=None,
                        help='target directory for RPM files')
    parser.add_argument('project', help='project name at PyPI or path')
    args = parser.parse_args()
    sys.exit(main(args.project, args.dist_dir))
