# -*- coding: utf-8 -*-

__all__ = ['POPEN_KW', 'Log', 'get_logs', 'get_log', 'get_revisions']


import os, sys, subprocess
from compat import xml2elem, strptime
from decoder import safe_decode

POPEN_ENV = os.environ.copy()
POPEN_ENV['LANG'] = 'C'

POPEN_KW = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=POPEN_ENV)


class Log(object):
    def __init__(self, url, rev):
        self.url = url
        self.rev = rev

        xml_data = self._prepare_info(self.url, self.rev)
        root = xml2elem(xml_data)
        entry = root.find('entry')
        self.url = entry.find('url').text
        self.root = entry.find('repository').find('root').text
        self.subpath = self.url[len(self.root):]

        xml_data = self._prepare_log(self.url, self.rev)
        root = xml2elem(xml_data)
        entry = root.find('logentry')
        self.author = entry.find('author').text
        self.date = strptime(entry.find('date').text[:19],'%Y-%m-%dT%H:%M:%S')
        self.msg = entry.find('msg').text

        paths = entry.find('paths')
        self.paths = [(x.attrib['action'], x.text) for x in paths]
        self.diff = self._process_diff(self.url, self.rev, paths)

        #self.normalized_paths = [
        #        (a, p[len(self.subpath):].lstrip('/'))
        #        for a,p in self.paths]

    def _prepare_info(self, url, rev):
        '''return `utf-8` xml data'''
        cmd = ['svn', 'info', '--xml']
        cmd.append('-r%s' % str(rev))
        cmd.append(url)
        status, out, err = command(cmd)
        return out

    def _prepare_log(self, url, rev):
        '''return `utf-8` xml data'''
        cmd = ['svn', 'log', '-v', '--xml']
        cmd.append('-r%s' % str(rev))
        cmd.append(url)
        status, out, err = command(cmd)
        return out

    def _prepare_diff(self, url, rev):
        '''return `unicode` text data'''

        cmd = ['svn', 'diff']
        try:
            rev_i = int(rev)
            prev_i = rev_i - 1
            cmd.append('-r%d:%d' % (prev_i, rev_i))
        except:
            cmd.append('-r%s' % rev)
        cmd.append(url)
        status, out, err = command(cmd)
        return safe_decode(out, per_line=True)

    def _process_diff(self, url, rev, path_set):
        need_diff = [x for x in path_set
                     if not (
                       x.attrib['action'] == 'D' or
                       (x.attrib['action'] == 'A' and
                        'copyfrom-path' in x.attrib)
                     )]

        if need_diff:
            return self._prepare_diff(url, rev)

        else:
            # copy or move or delete only
            diffs = []
            for path in path_set:
                attrib = path.attrib
                if attrib['action'] == 'A':
                    diff = 'Copied: %s\n   from %s (rev %s)' % (
                                path.text,
                                attrib['copyfrom-path'],
                                attrib['copyfrom-rev'],
                            )
                elif attrib['action'] == 'D':
                    diff = 'Deleted: %s' % path.text
                diffs.append(diff)

            return '\n'.join(diffs)

    def __repr__(self):
        return "<Log rev=%s, url='%s'>" % (str(self.rev), str(self.url))


def get_logs(url, rev=None, rev2=None):
    """
    >>> url = 'http://svn.example.com/repos/path'
    >>> get_logs(url, 1)
    [<Log rev=1, ...>]
    >>> get_logs(url, 1, 2)
    [<Log rev=1, ...>, <Log rev=2, ...>]
    >>> get_logs(url, 1, 3)
    [<Log rev=1, ...>, <Log rev=2, ...>, <Log rev=3>]
    >>> get_logs(url, 1, 'HEAD')
    [<Log rev=1, ...>, <Log rev=2, ...>, ..., <Log rev=10>]
    """
    cmd = ['svn', 'log', '--xml']
    if rev and rev2:
        cmd.append('-r%s:%s' % (str(rev), str(rev2)))
    elif rev:
        cmd.append('-r%s' % str(rev))
    cmd.append(url)
    status, out, err = command(cmd)
    root = xml2elem(out)
    return [Log(url, node.attrib['revision']) for node in root]


def get_log(url, rev):
    return get_logs(url, rev)[0]


def get_revisions(urls, rev=None):
    """
        >>> urls = ['http://svn.example.com/repos/path1',
        ...         'http://svn.example.com/repos/path2']

    No `rev` supplied, get_revisions return all revisions for urls.

        >>> get_revisions(urls)
        [1,2,3,5]

    If `rev` supplied, get_revisions collect logs by 'svn -r rev:HEAD',
    then returned revisions include `rev` revision.

        >>> get_revisions(urls, 3)
        [3,5]

    If `rev` is greater then repository's newest revision, get_revisions
    return empty list.

        >>> get_revisions(urls, 6)
        []

    Another call samples:

        >>> get_revisions(urls, None)
        [1,2,3,5]
        >>> get_revisions(urls, 0)
        [1,2,3,5]
        >>> get_revisions(urls, '0')
        [1,2,3,5]
        >>> get_revisions(urls, '3')
        [3,5]
        >>> get_revisions(urls, 5)
        [5]
        >>> get_revisions(urls, '6')
        []
    """
    revs = set()
    for url in urls:
        cmd = ['svn', 'log', '--xml']
        if rev:
            cmd.append('-r%s:HEAD' % str(rev))
        cmd.append(url)
        status, out, err = command(cmd)
        if status == 0:
            root = xml2elem(out)
            revs.update(int(node.attrib['revision']) for node in root)

    return sorted(revs)

def command(cmd):
    '''command return communication data by `utf-8` '''
    #print "#DEBUG#", cmd   #FIXME: we need --debug option
    proc = subprocess.Popen(cmd, **POPEN_KW)
    out, err = proc.communicate()
    proc.wait()
    out = safe_decode(out, per_line=True).encode('utf-8')
    return proc.returncode, out, err

