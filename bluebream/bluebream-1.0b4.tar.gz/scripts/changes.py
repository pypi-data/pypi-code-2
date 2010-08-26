#!/usr/bin/env python
import ConfigParser
import cStringIO
import subprocess
import sys
import re
import os

OLD_VERSIONS = 'releases/zope-3.4.0.cfg'
NEW_VERSIONS = 'releases/bluebream-1.0a2.cfg'

def get_package(old_versions=OLD_VERSIONS,
                new_versions=NEW_VERSIONS):
    cp = ConfigParser.ConfigParser()
    cp.read(old_versions)
    old_pkg_versions = cp._sections['versions']

    cp = ConfigParser.ConfigParser()
    cp.read(new_versions)
    new_pkg_versions = cp._sections['versions']
    for package, version in new_pkg_versions.items():
        if package not in old_pkg_versions:
            yield package, '0.0.0'
        else:
            yield package, old_pkg_versions[package]

def extract_changes(package, version):
    url = 'svn://svn.zope.org/repos/main/%s/trunk/CHANGES.txt' % package
    changes = subprocess.Popen(['svn', 'cat', url, package],
                               shell=False,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    changes.wait()
    if changes.returncode > 0:
        print changes.stderr.read()
    diff = open(os.path.join("releases", package+"-changes.txt"), 'w')
    underline = "="*len(package)
    diff.write(package)
    diff.write('\n')
    diff.write(underline)
    diff.write('\n\n')
    pattern_start = re.compile('\d+\.\d+\.\d+\s+.*\d\d\d\d.\d\d.\d\d.*')
    pattern_end = re.compile('%s\s+.*\d\d\d\d.\d\d.\d\d.*'%version)
    started = False
    for line in changes.stdout:
        if not started:
            if pattern_start.match(line):
                started = True
            else:
                continue
        if pattern_end.match(line):
            break
        else:
            diff.write(line)
    diff.close()

if __name__ == '__main__':
    for pkg in get_package():
        extract_changes(*pkg)
