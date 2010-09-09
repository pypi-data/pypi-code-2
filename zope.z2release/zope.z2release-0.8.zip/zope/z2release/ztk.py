"""
Generate an index file based on the ztk-versions.cfg file of the Zope Toolkit
in order to provide a version specific index page generated to be used
in combination with easy_install -i <some_url>

Usage:

cli.py tags/1.0a1 /tmp/index/1.0a1
cli.py branches/1.0 /tmp/index/1.0
"""

import os
import sys
import urllib
from xmlrpclib import Server

from zope.z2release.utils import CasePreservingConfigParser
from zope.z2release.utils import write_index


def main():
    if len(sys.argv) != 3:
        print 'Usage: ztk_kgs <tag-name> <destination-dirname>'
        print 'Example: ztk_kgs tags/1.0a1 /var/www/download.zope.org/zopetoolkit/index/1.0a1/' 
        sys.exit(1)

    tag = sys.argv[1]
    dirname = sys.argv[2]
    if not os.path.exists(dirname):
        print >>sys.stderr, 'Creating index directory: %s' % dirname
        os.makedirs(dirname)

    version = tag.split('/')[-1]
    versions_url = 'http://svn.zope.org/*checkout*/zopetoolkit/%s/ztk-versions.cfg' % tag
    print >>sys.stderr, 'Fetching %s' % versions_url
    data = urllib.urlopen(versions_url).read()
    version_file = os.path.join(dirname, 'ztk-versions.cfg')
    file(version_file, 'w').write(data)

    app_versions_url = 'http://svn.zope.org/*checkout*/zopetoolkit/%s/zopeapp-versions.cfg' % tag
    print >>sys.stderr, 'Fetching %s' % app_versions_url
    data = urllib.urlopen(app_versions_url).read()
    app_version_file = os.path.join(dirname, 'zopeapp-versions.cfg')
    file(app_version_file, 'w').write(data)

    # CP = CasePreservingConfigParser()
    # CP.read(version_file)
    # 
    # server = Server('http://pypi.python.org/pypi')
    # 
    # for package in CP.options('versions'):
    #     version = CP.get('versions', package)
    #     if '#' in version:
    #         version = version.split('#')[0].strip()
    #     write_index(server, package, version, dirname)

if __name__ == '__main__':
    main()
