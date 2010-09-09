"""
Generate an index file based on the version.cfg file of Zope 2
in order to provide a version specific index page generated to be used
in combination with easy_install -i <some_url>

Usage:

cli.py tags/2.12.0a3 /tmp/index/2.12.0a3
cli.py branches/2.12 /tmp/index/2.12

"""

import os
import sys
import urllib
from xmlrpclib import Server

from zope.z2release.utils import CasePreservingConfigParser
from zope.z2release.utils import write_index


def fetch_cfg(url, version_file):
    print >>sys.stderr, 'Fetching %s' % url
    data = urllib.urlopen(url).read()
    file(version_file, 'w').write(data)


def write_versions(version_file, server, dirname):
    CP = CasePreservingConfigParser()
    CP.read(version_file)
    for package in CP.options('versions'):
        version = CP.get('versions', package)
        if '#' in version:
            version = version.split('#')[0].strip()
        write_index(server, package, version, dirname)
    return CP


def build_version_file(name, dirname, url, server):
    version_file = os.path.join(dirname, name)
    fetch_cfg(url, version_file)
    return write_versions(version_file, server, dirname)


def main():
    if len(sys.argv) != 3:
        print 'Usage: z2_kgs <tag-name> <destination-dirname>'
        print 'Example: z2_kgs tags/2.12.1 /var/www/download.zope.org/Zope2/index/2.12.1/'
        sys.exit(1)

    tag = sys.argv[1]
    dirname = sys.argv[2]
    if not os.path.exists(dirname):
        print >>sys.stderr, 'Creating index directory: %s' % dirname
        os.makedirs(dirname)

    server = Server('http://pypi.python.org/pypi')

    url = 'http://svn.zope.org/*checkout*/Zope/%s/versions.cfg' % tag
    CP = build_version_file('versions.cfg', dirname, url, server)

    buildout = CP.options('buildout')
    if 'extends' in buildout:
        url = CP.get('buildout', 'extends')
        name = 'ztk-versions.cfg'
        if 'http' in url and not '\n' in url and url.endswith(name):
            build_version_file(name, dirname, url, server)


if __name__ == '__main__':
    main()
