"""
gravy.py - basic VCS repository abstraction
===========================================

This is a simple facade over the mercurial command-line client. Handles git
repos if the hg-git extension is installed.

Requires `pip` at the minute.

Local Caching
-------------

`repo.clone()` will do the initial download of the (assumed to be remote)
repository and cache to the filesystem.  Subsequent interaction is via this
local copy.

By default, repos are stored in '~/.gravy' unless initialized with
'cache=False', in which case a temporary directory is used.

Further calls to `repo.clone()` will be ignored as long as the cached copy
exists. `repo.flush()` will delete the cached copy entirely.

"""

import os
import sys
import re
import shutil
import urllib
from os.path import dirname, basename, abspath, splitext
from os.path import exists as pathexists, join as pathjoin
from urlparse import urlparse
from fnmatch import fnmatch

from pip import logger, call_subprocess, InstallationError


schemes = {
    ('ssh', 'git'): 'git+ssh://git@',
    ('https', 'git'): 'git+https://',
    ('http', 'git'): 'git+https://',
    ('ssh', 'hg'): 'ssh://hg@',
    ('https', 'hg'): 'https://',
    ('http', 'hg'): 'https://',
    ('git', 'git'): 'git://',
}
scheme_for = dict((val, key) for (key, val) in schemes.items())

def get_storage_root():
    try:
        root = os.path.expanduser('~')
    except:
        pass
    root = root or os.getenv('HOME') or os.getcwd()
    return pathjoin(root, '.gravy')

STORAGE_ROOT = get_storage_root()
del get_storage_root
VCS_TYPES = set(['hg', 'git', 'bzr', 'svn'])
REPO_IGNORE_SET = set('.'+vcs for vcs in VCS_TYPES)

def ignore_repo_dirs(src, names):
    """
    A filter for `shutil.copytree` which ignores typical repo directories
    """
    return REPO_IGNORE_SET

def call(cmd, **kw):
    """
    wraps `pip.call_subprocess()`
    """
    try:
        return call_subprocess(cmd, **kw)
    except InstallationError, e:
        raise RuntimeError(str(e))

def urlsplit(url):
    scheme, divider, url = url.partition('://')
    scheme = scheme or 'https'
    ssh_user, divider, tail = url.partition('@')
    if ssh_user == 'git':
        scheme = 'git+' + scheme
    if tail:
        url = tail
    try:
        k = scheme + '://'
        if divider and ssh_user:
            k = k + ssh_user + divider
        scheme, vcs = scheme_for[k]
    except KeyError, e:
        vcs = ''
    path_parts = url.strip('/').split('/')
    d = len(path_parts)
    if d:
        domain = path_parts[0]
    else:
        domain = ''
    if d < 3:
        user = slug = ''
        path = '/'.join(path_parts[1:])
    elif domain == 'gitorious.org':
        if d < 4:
            user = ''
            slug = path_parts[1]
            path = '/'.join(path_parts[2:])
        else:
            user = path_parts[1].lstrip('~')
            slug = path_parts[2]
            path = '/'.join(path_parts[3:])
        vcs = 'git'
    elif domain == 'github.com' or domain == 'bitbucket.org':
        user = path_parts[1]
        slug = path_parts[2]
        path = '/'.join(path_parts[3:])
        if domain == 'github.com':
            vcs = 'git'
        else:
            vcs = 'hg'
    else:
        user = ''
        slug = path_parts[1]
        path = '/'.join(path_parts[2:])
    if not vcs and domain.count('.') > 1:
        vcs = domain.split('.', 1)[0]
    slug_parts = splitext(slug)
    if slug_parts[1] in REPO_IGNORE_SET:
        slug = slug_parts[0]
    return vcs, scheme, domain, user, slug, path

rx_py_modules = re.compile(
    r'^[^#]*\bpy_modules\b\s*?=\s*?[\[](?P<modules>.*?)[\]]',
    re.DOTALL | re.MULTILINE
)

rx_py_packages = re.compile(
    r'^[^#]*\bpackages\b\s*?=\s*?[\[](?P<packages>.*?)[\]]',
    re.DOTALL | re.MULTILINE
)

rx_py_package_dir = re.compile(
    r'^[^#]*\bpackage_dir\b\s*?=\s*?[{](?P<package_dir>.*?)[}]',
    re.DOTALL | re.MULTILINE
)

def find_py_packages(setup_py):
    """
    >>> find_py_packages("packages=['mylib']")
    {'mylib': 'mylib'}
    >>> find_py_packages("packages=['mylib']\\npackage_dir = {'mylib': 'src'}")
    {'mylib': 'src'}
    >>> find_py_packages("packages=['pip', 'pip.commands', 'pip.vcs'],")
    {'pip': 'pip'}
    >>> find_py_packages("#COMMENT\\n\\npackages=['pip', 'pip.commands', 'pip.vcs'],")
    {'pip': 'pip'}
    >>> find_py_packages('description="packages"\\npy_modules=["myscript"]')
    {}
    """
    matches = list(rx_py_packages.finditer(setup_py))
    ret = {}
    if matches:
        for m in matches[-1].group('packages').split(','):
            m = m.strip().strip('"').strip("'")
            if m and '.' not in m:
                ret[m] = m
    matches = list(rx_py_package_dir.finditer(setup_py))
    if matches:
        for m in matches[-1].group('package_dir').split(','):
            try:
                k, v = [x.strip().strip('"').strip("'").strip() for x in m.split(':', 1)]
            except ValueError:
                continue
            else:
                if k:
                    ret[k] = v
    return ret

def find_py_modules(setup_py):
    """
    Search a setup.py file for a py_modules settings.

    Expects an explicit list-of-strings declaration, eg.
    
        setup(
            ...
            py_modules=['this', 'that'],
            ...
        )

    Obviously far from foolproof, but better than nothing.

    >>> find_py_modules("#    py_modules=['myscript']")
    >>> find_py_modules("py_modules=[]")
    []
    >>> find_py_modules("py_modules=[\\n]")
    []
    >>> find_py_modules("py_modules=['myscript']")
    ['myscript']
    >>> s = "py_modules=[],\\n    py_modules=['myscript',\\n 'otherscript' ]"
    >>> sorted(find_py_modules(s))
    ['myscript', 'otherscript']

    """
    matches = list(rx_py_modules.finditer(setup_py))
    if matches:
        ret = []
        for m in matches[-1].group('modules').split(','):
            m = m.strip().strip('"').strip("'")
            if m:
                ret.append(m)
        return ret

class RepositoryBase(object):
    """
    Base Repository abstraction for a locally-cached repo.

    """

    def __init__(self, url, cache=True, path=None):
        self._url = url
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if parsed.netloc:
            path_parts.insert(0, parsed.netloc)
        item = path_parts[0]
        # remove hg@ etc.
        path_parts[0] = item[item.find('@')+1:]
        # remove leading tilde from user name (gitorious)
        path_parts[1] = path_parts[1].lstrip('~')
        self.name = path_parts[-1]
        self.relpath = '/'.join(path_parts)
        if not cache:
            assert not path, "setting path is redundant if cache=False"
            path = self._tempdir()
        elif not path:
            path = '%s/%s' % (STORAGE_ROOT, self.relpath)
        self._path = path.rstrip('/') + '/'

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self.name)
        
    def _tempdir(self):
        """
        Create a temp directory with tempfile as normal, but return the name of
        a yet-to-be-created subdirectory within it.

        `hg clone` doesn't care if the target directory exists or not, but
        `shutil.copytree` will fail if the directory does exist - this function
        handles both scenarios.
        """
        import tempfile
        prefix = 'gravy-%s-' % self.name
        return '%s/%s' % (
            tempfile.mkdtemp(prefix=prefix), self.name
        )

    @property
    def url(self):
        """
        The url of the remote repository
        """
        return self._url

    @property
    def path(self):
        """
        The filesytem path of the local copy
        """
        return self._path

    def flush(self):
        """
        Delete the local copy entirely
        """
        if pathexists(self._path):
            shutil.rmtree(self._path)

    def cmd(self, args):
        """
        call a subprocess with `self.path` as the working directory
        """
        return call(args, cwd=self._path, show_stdout=False)

    def cmd_split(self, args):
        """
        Split whitespace-divided command output into a list of 2-element tuples
        """
        raw = self.cmd(args)
        ret = []
        if raw:
            for line in raw.splitlines():
                parts = line.split()
                ret.append((' '.join(parts[:-1]), parts[-1]))
        return ret

    def pathto(self, *args):
        return self._path + '/'.join(arg.strip('/') for arg in args)

    def listdir(self, top=''):
        """
        `os.listdir` of a repository directory or optional 'top' subdirectory
        """
        if top:
            return os.listdir(self.pathto(top))
        return os.listdir(self._path)

    def remotecopy(self, dest=None):
        """
        Create a new clone of the remote repository.
        
        This is a temporary copy unless 'dest' is given.
        """
        if dest:
            other = self.__class__(self.url, path=dest)
        else:
            other = self.__class__(self.url, cache=False)
        other.clone()
        return other

    def copy(self, dest=None):
        """
        Create a new Repository based on the current Repository

        Fails if dest exists.
        """
        dest = dest or self._tempdir()
        self.copyfiles(dest, ignore=None)
        return self.__class__(self.url, path=dest)

    def copyfiles(self, dest, root=None, symlinks=False, ignore=ignore_repo_dirs):
        """
        Recursive copy of the repository files to `dest`.
        
        By default ignores '.hg', '.git' etc., set ignore=None to copy all.
        """
        src = self._path + (root or '').lstrip('/')
        shutil.copytree(src, dest, symlinks=symlinks, ignore=ignore)

    def copyfile(self, src, dest):
        """
        Copy file 'src' to file 'dest'.

        Creates destination directories as required.
        """
        dir = dirname(dest)
        if not pathexists(dir):
            os.makedirs(dir)
        src = self._path + src.lstrip('/')
        shutil.copyfile(src, dest)
        shutil.copymode(src, dest)

    _ignore = ['test*', 'example*', 'demo/*', 'demos/*', 'doc/*', 'docs/*']

    def find_py_files(self, ignore=_ignore):
        """Return all Python packages and modules found within the repo

        Unlike `setuptools.find_packages()` this only returns top-level packages,
        not sub-packages.

        The patterns in `ignore` are taken to be relative to the repository root.
        """
        # the complicating issue here is that you might have an "ext" directory, say,
        # which is not itself a python package, but which contains python packages
        # and which is within a python package, so you can't break from the first
        # loop whenever a package is found, you have to walk the whole tree.
        root = self.path
        d = len(root)
        pkg_ignore = set()
        module_ignore = set()
        if ignore:
            for patt in ignore:
                pkg_ignore.add(root+patt)
                module_ignore.add(root+patt)
                if not patt.startswith('*/'):
                    module_ignore.add(root+'*/'+patt)
        pkgset = set()
        packages = {}
        modules = {}
        setup_py = None
        for parent, dirs, files in os.walk(root):
            parent_dir = parent + '/'
            if '__init__.py' in files:
                m = any(fnmatch(parent_dir, p) for p in pkg_ignore)
                if not (m or dirname(parent) in pkgset):
                    relpath = parent[d:]
                    packages[basename(relpath)] = relpath
                pkgset.add(parent)
            elif not any(fnmatch(parent_dir, p) for p in module_ignore):
                for f in files:
                    if f == 'setup.py':
                        # only the first file encountered
                        setup_py = setup_py or pathjoin(parent, f)
                    elif f.endswith('.py') and not f.startswith('ez_setup'):
                        fpath = pathjoin(parent[d:], f)
                        modules[basename(fpath)[:-3]] = fpath
        # if there was a setup.py, do a naive parse and defer to any results that
        # it returns, otherwise return what we found by walking the tree
        if setup_py:
            text = ''
            with open(setup_py) as fp:
                text = fp.read()
            py_modules = find_py_modules(text)
            if py_modules is not None:
                modules = dict((X, X.replace('.', '/')+'.py') for X in py_modules)
            packages = find_py_packages(text) or packages
        return {'packages': packages.items(), 'modules': modules.items()}

class HgRepo(RepositoryBase):
    """
    Mercurial Repository facade.

    Methods are named after the mercurial equivalents. `hg help` for info.
    Handles git repositories if the hg-git extension is installed
    """

    @classmethod
    def from_bitbucket(cls, owner, slug, scheme='ssh', **kw):
        url = '%sbitbucket.org/%s/%s' % (schemes[(scheme, 'hg')], owner, slug)
        return cls(url, **kw)

    @classmethod
    def from_github(cls, owner, slug, scheme='ssh', **kw):
        url = '%sgithub.com/%s/%s.git' % (schemes[(scheme, 'git')], owner, slug)
        return cls(url, **kw)

    @classmethod
    def from_gitorious(cls, owner, slug, scheme='git', **kw):
        netloc = 'gitorious.org'
        if scheme == 'https':
            netloc = 'git.' + netloc
        url = '%s%s/~%s/%s/%s.git' % (schemes[(scheme, 'git')], netloc, owner, slug, slug)
        return cls(url, **kw)

    def __init__(self, *args, **kw):
        super(HgRepo, self).__init__(*args, **kw)
        self._incoming = dirname(self._path).rsplit('.', 1)[0] + '.incoming'
        if not pathexists(self._incoming):
            os.makedirs(self._incoming)

    def _incoming_file_name(self, source=None):
        source = source or self._url
        return pathjoin(self._incoming, urllib.quote(source, safe=''))

    def del_incoming(self, source=None):
        f = self._incoming_file_name(source)
        if pathexists(f):
            os.remove(f)

    def flush_incoming(self):
        if pathexists(self._incoming) and os.listdir(self._incoming):
            shutil.rmtree(self._incoming)
        if not pathexists(self._incoming):
            os.makedirs(self._incoming)

    def flush(self):
        self.flush_incoming()
        super(HgRepo, self).flush()

    def clone(self, fresh=False, **kw):
        """
        Clone the remote repository if doesn't exist locally or fresh=True
        """
        if fresh or not pathexists(self._path) or not os.listdir(self._path):
            dir = dirname(self._path)
            if not pathexists(dir):
                os.makedirs(dir)
            call(['hg', 'clone', self._url, self._path], **kw)

    def checkout(self, node_tag_or_revision):
        """
        Update the local repo to a branch, tag or revision
        """
        self.cmd(['hg', 'update', '-C', node_tag_or_revision])

    def incoming(self, source=None, revision=None, show_patch=False, bundle=True):
        self.del_incoming(source)
        args = ['hg', 'incoming']
        if revision:
            args.extend(['-r', revision])
        if show_patch:
            args.append('--patch')
        if bundle:
            args.extend(['--bundle', self._incoming_file_name(source)])
        if source:
            args.append(source)
        try:
            return self.cmd(args)
        except RuntimeError:
            return ''

    def outgoing(self, dest=None, revision=None):
        args = ['hg', 'outgoing']
        if revision:
            args.extend(['-r', revision])
        if dest:
            args.append(dest)
        try:
            return self.cmd(args)
        except RuntimeError:
            return ''

    def commit(self, msg):
        args = ['hg', 'commit', '-m', '"%s"' % msg]
        self.cmd(args)

    def pull(self, source=None, revision=None, update=False):
        args = ['hg', 'pull']
        if revision:
            args.extend(['-r', revision])
        if update:
            args.append('--update')
        bundle = self._incoming_file_name(source)
        if pathexists(bundle):
            source = bundle
        if source:
            args.append(source)
        self.cmd(args)

    def revert(self, target, revision=None, backup=True):
        args = ['hg', 'revert']
        if not backup:
            args.append('--no-backup')
        if revision:
            args.extend(['-r', revision])
        args.append(target)
        self.cmd(args)

    def revertall(self, revision=None, backup=True):
        self.revert('--all', revision, backup)

    def rollback(self):
        self.cmd(['hg', 'rollback'])

    @property
    def branches(self, **opts):
        return self.cmd_split(['hg', 'branches'])

    @property
    def tags(self, **opts):
        return self.cmd_split(['hg', 'tags'])

    def branch(self, name=None):
        args = ['hg', 'branch']
        if name:
            args.append(name)
            self.cmd(args)
        else:
            return self.cmd(args).strip()

    def branchmap(self):
        return dict(self.branches)

    def status(self):
        return self.cmd(['hg', 'status'])

    def remove(self, target):
        self.cmd(['hg', 'remove', target])

provider_dispatch = {
    'bitbucket': HgRepo.from_bitbucket,
    'bitbucket.org': HgRepo.from_bitbucket,
    'github': HgRepo.from_github,
    'github.com': HgRepo.from_github,
    'gitorious': HgRepo.from_gitorious,
    'gitorious.org': HgRepo.from_gitorious,
}
vcs_dispatch = {
    'hg': HgRepo,
    'mercurial': HgRepo,
    'git': HgRepo,
}

def anyrepo(*args, **kw):
    """
    Create a Repo for the appropriate VCS.

    one arg - it's a url, try to guess the VCS type
    two args - it's a (vcstype, url) pair, choose from `vcs_dispatch`
    three args - it's a (provider, owner, slug) triple, choose from `provider_dispatch`
    """
    d = len(args)
    if d == 1:
        return HgRepo(args[0], **kw)
    elif d == 2:
        try:
            cls = vcs_dispatch[args[0]]
        except KeyError:
            raise Exception("unsupported version control system '%s'" % args[0])
        else:
            return cls(args[1])
    elif d == 3:
        provider = args[0].rpartition('://')[2].strip('/')
        try:
            func = provider_dispatch[provider]
        except KeyError:
            #raise Exception("unsupported provider '%s'" % args[0])
            url = provider
            if not url.startswith('http'):
                url = 'http://' + url
            url = url.rstrip('/') + '/' + (args[1] or '')
            url = url.rstrip('/') + '/' + (args[2] or '')
            return anyrepo(url, **kw)
        else:
            return func(*args[1:], **kw)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

