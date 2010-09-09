import os
import sys
import urlparse

from ConfigParser import RawConfigParser as ConfigParser


class CasePreservingConfigParser(ConfigParser):

    def optionxform(self, option):
        return option  # don't flatten case!


def write_index(server, package, version, dirname):
    if '-' in package:
        exists = server.search(dict(name=package))
        if not exists:
            package = package.replace('-', '_')

    print >>sys.stderr, 'Package %s==%s' % (package, version)
    dest_dir = os.path.join(dirname, package)
    if os.path.exists(dest_dir):
        print >>sys.stderr, "Don't override package %s==%s" % (package, version)
        return

    os.makedirs(dest_dir)
    index_html = os.path.join(dest_dir, 'index.html')

    fp = file(index_html, 'w')
    print >>fp, '<html><body>'
    lst = server.release_urls(package, version)
    if lst:
        # package hosted on PyPI
        for d in lst:
            link = '<a href="%s">%s</a>' % (d['url'], d['filename'])
            print >>fp, link
            print >>fp, '<br/>'
    else:
        # for externally hosted packages we need to rely on the
        # download_url metadata
        rel_data = server.release_data(package, version)
        download_url = rel_data['download_url']
        if download_url == 'UNKNOWN':
            raise RuntimeError('Incorrect download_url for package %s' % package)
        filename = os.path.basename(urlparse.urlparse(download_url)[2])
        link = '<a href="%s">%s</a>' % (download_url, filename)
        print >>fp, link

    print >>fp, '</body></html>'
    fp.close()
