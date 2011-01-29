# This file is part of the egoboost package which is release under the MIT
# License. You can find the full text of the license in the LICENSE file.
# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

import lxml.html
import lxml.etree
import re
import urllib2
import xmlrpclib

VERSION_REG = re.compile(r'(\d+\.\d+(\.\d+)*([ab]\d+)?)')

def get_pypi_downloads(name, show_hidden=True):
    """
    Fetches PyPi download statistics via XMLRPC.

    >>> get_pypi_downloads('python-amazon-product-api')
    {'0.2.0': {'python-amazon-product-api-0.2.0.tar.gz': 68,
               'python-amazon-product-api-0.2.0.win32-py2.5.exe': 15,
               'python-amazon-product-api-0.2.0.win32-py2.5.msi': 17,
               'python-amazon-product-api-0.2.0.win32-py2.6.exe': 17,
               'python-amazon-product-api-0.2.0.win32-py2.6.msi': 19},
     '0.2.1': {'python-amazon-product-api-0.2.1.tar.gz': 130},
     '0.2.2': {'python-amazon-product-api-0.2.2.tar.gz': 101,
               'python-amazon-product-api-0.2.2.win32.exe': 29},
     '0.2.3': {'python-amazon-product-api-0.2.3.tar.gz': 90,
               'python-amazon-product-api-0.2.3.win32-py2.5.exe': 7}}
    """
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    def fetch_downloads(rel):
        return dict((data.get('filename'), data.get('downloads'))
            for data in client.release_urls(name, rel))
    return dict((release, fetch_downloads(release))
        for release in client.package_releases(name, show_hidden))

def get_bitbucket_downloads(user, repo):
    """
    Parses bitbucket.org repository download page for download counts.

    >>> get_bitbucket_downloads('basti', 'python-amazon-product-api')
    {'0.2.0': {'python-amazon-product-api-0.2.0.tar.gz': 2303},
     '0.2.1': {'python-amazon-product-api-0.2.1.tar.gz': 2138},
     '0.2.2': {'python-amazon-product-api-0.2.2.tar.gz': 1758},
     '0.2.3': {'python-amazon-product-api-0.2.3.tar.gz': 1138}}
    """
    url = 'http://bitbucket.org/%(user)s/%(repo)s/downloads' % locals()
    fp = urllib2.urlopen(url)
    root = lxml.html.parse(fp).getroot()
    downloads = root.xpath("//tr[starts-with(@id, 'download-')]")

    TIMES_REG = re.compile(r'(\d+) times')

    counts = {}
    for tag in downloads:
        tds = tag.xpath('td')
        filename = tds[0].text_content().strip()
        try:
            count = int(TIMES_REG.search(tds[4].text_content().strip()).group(1))
            version = VERSION_REG.search(filename).group(1)
            if version not in counts:
                counts[version] = {filename : count}
            else:
                counts[version][filename] = count
        except AttributeError:
            continue
    return counts

def get_github_downloads(user, repo):
    """
    Parses github.com repository download page for download counts.

    >>> get_github_downloads('redtoad', 'python-amazon-product-api')
    {'0.2.0': {'python-amazon-product-api-0.2.0.tar.gz': 2303},
     '0.2.1': {'python-amazon-product-api-0.2.1.tar.gz': 2138},
     '0.2.2': {'python-amazon-product-api-0.2.2.tar.gz': 1758},
     '0.2.3': {'python-amazon-product-api-0.2.3.tar.gz': 1138}}
    """
    url = 'http://github.com/%(user)s/%(repo)s/downloads' % locals()
    fp = urllib2.urlopen(url)
    root = lxml.html.parse(fp).getroot()
    downloads = root.xpath("//ol[@id='manual_downloads']/li")
    
    TIMES_REG = re.compile('(\d+) downloads')

    counts = {}
    for tag in downloads:
        try:
            filename = tag.xpath('h4')[0].text_content().strip()
            downloads = tag.xpath("span[@class='download-stats']")[0].text_content()
            count = int(TIMES_REG.search(downloads).group(1))
            version = VERSION_REG.search(filename).group(1)
            if version not in counts:
                counts[version] = {filename : count}
            else:
                counts[version][filename] = count
        except (AttributeError, IndexError):
            continue
    return counts

PATH_REGS = [
    (re.compile('http://pypi.python.org/pypi/(?P<pkg>[\w-]+)/?'),
        get_pypi_downloads), 
    (re.compile('http://bitbucket.org/(?P<user>\w+)/(?P<repo>[\w-]+)/?'),
        get_bitbucket_downloads),
    (re.compile('http://github.com/(?P<user>\w+)/(?P<repo>[\w-]+)/?'),
        get_github_downloads),
]
    
def get_downloads(url):
    """
    Fetches download statistics from URL. If URL does not match any know 
    pattern, a ``ValueError`` is raised.
    """
    for regex, fnc in PATH_REGS:
        m = regex.search(url)
        if m: return fnc(*m.groups())
    raise ValueError

if __name__ == '__main__':

    import simplejson as json
    import sys

    for path in sys.argv[1:]:
        data = get_downloads(path)
        print json.dumps(data)

