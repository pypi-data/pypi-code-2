from gocept.munin.client import SimpleGraph, SimpleMultiGraph, main
from os.path import isdir, basename, abspath, normpath, join, exists
from os import environ, getcwd, symlink
from inspect import isclass
from socket import gethostname
from sys import argv


class zcasyncqueusize(SimpleGraph):
    key = 'queuesize'
    name = 'Job_queue_size'
    title = 'zc.async Job Queue Size'
    category = 'zc.async'

class zcasyncjobstatistics(SimpleMultiGraph):
    keys = ['started', 'successful', 'failed', 'unknown']
    names = ['Started_jobs', 'Successful_jobs', 'Failed_jobs', 'Unknown_jobs']
    title = 'zc.async Job Statistics'
    category = 'zc.async'

class zcasynctimestatistics(SimpleMultiGraph):
    keys = ['longest_successful', 'shortest_successful',
            'longest_failed', 'shortest_failed']
    names = ['Longest_successful', 'Shortest_successful',
             'Longest_failed', 'Shortest_failed']
    title = 'zc.async Time Statistics'
    category = 'zc.async'


def install(script, cmd, path, prefix=None, suffix=None):
    """ set up plugin symlinks using the given prexix/suffix or the
        current hostname and directory """
    assert isdir(path), 'please specify an existing directory'
    if prefix is None:
        prefix = gethostname()
    if suffix is None:
        suffix = basename(getcwd())
    source = abspath(script)
    for name, value in globals().items():
        if isclass(value) and value.__module__ == __name__:
            plugin = '_'.join((prefix, name, suffix))
            target = normpath(join(path, plugin))
            if not exists(target):
                symlink(source, target)
                print 'installed symlink %s' % target
            else:
                print 'skipped existing %s' % target


def run(ip_address='localhost', http_address=8080, port_base=0, user=None):
    if 3 <= len(argv) <= 5 and argv[1] == 'install':
        return install(*argv)
    if not 'URL' in environ:
        port = int(http_address) + int(port_base)
        host = '%s:%d' % (ip_address, port)
        environ['URL'] = 'http://%s/@@munin.async.plugins/%%s' % host
    if not 'AUTH' in environ and user is not None:
        environ['AUTH'] = user
    main()
