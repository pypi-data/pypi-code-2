#!/usr/bin/env python

import os, sys, re
import socket
import subprocess
import datetime
#import logging
#from logging import log, info, debug, warn

import yaml

import simplejson as json
import wsgiserver
import jsonrpc2
import urllib2
import urllib

from bzrlib.branch import Branch
from bzrlib.errors import NotBranchError
from bzrlib.plugin import load_plugins

from automa.path import Path
from automa import sh, cd, options
from automa.log import *
import cmdutils

DEFAULT_PORT   = 8090
DEFAULT_HOST   = '0.0.0.0'
DEFAULT_CONFIG = '~/.bazaar/bzrsync.yaml'

this_host = socket.gethostname()

def is_bzr_branch(path):
    if not isinstance(path, Path):
        path = Path(path)
    try:
        branch, inpath = Branch.open_containing(path.pathname)
        if inpath != '':
            return False
    except NotBranchError:
        return False
    return True

class BranchInfo(object):
    def __init__(self, repo, abspath):
        assert isinstance(repo, Path)
        assert isinstance(abspath, Path)
        self.repo    = repo
        self.abspath = abspath
        self.relpath = abspath.relativeto(repo)

    def __str__(self):
        return "%s" % self.abspath

    def __repr__(self):
        return "<BranchInfo repo:%s rel:%s abs:%s>" % (self.repo, self.relpath, self.abspath)

def _get_branches(root, topdir, exclude_childs=None):
    assert isinstance(root, Path)
    branches = []

    if topdir is None:
        return []

    if not isinstance(topdir, Path):
        topdir = Path(topdir)
    assert isinstance(topdir, Path)

    #debug("\n\n_get_branches(%s, %s, exclude:%s)" % (root, topdir, repr(exclude_childs)))
    for child in topdir.listdir():
        assert isinstance(child, Path)

        abschild = topdir / child
        assert isinstance(abschild, Path)

        if not abschild.isdir:
            continue
        if child.basename in ('.bzr', '.', '..',):
            continue

        #debug("  child:%s (abs:%s)" % (child, abschild))
        skip_this = False
        if exclude_childs:
            for x_child in exclude_childs:
                if not isinstance(x_child, Path):
                    x_child = Path(x_child)
                if not x_child.pathname.startswith('/'):
                    x_child = Path(root / x_child.pathname)
                assert isinstance(x_child, Path)
                if x_child.exists and (abschild.samefile(x_child) or abschild.same(x_child)):
                    #debug("\n\nSkipping excluded %s\n\n" % abschild)
                    skip_this = True
                    break

        if skip_this:
            continue

        if is_bzr_branch(abschild):
            #debug("  child %s (abs:%s) is BRANCH" % (child, abschild))
            assert Path(abschild / '.bzr').exists
            branches.append(BranchInfo(root, abschild))

        child_branches = _get_branches(root, abschild)
        #debug("  child %s (abs:%s) children branches:%s" % (child, abschild, repr(child_branches)))
        branches += child_branches

    return branches

def get_branches(repo, exclude_childs=None):
    return _get_branches(repo, repo, exclude_childs=exclude_childs)

def ping(host):
    ret = subprocess.call("ping -q -c 2 %s" % host,
                          shell=True,
                          stdout=open('/dev/null', 'w'),
                          stderr=subprocess.STDOUT)
    return (ret == 0)

def expand_pattern_list(pattern_list, exclude_pattern_list=None):
    exclude_pattern_list = exclude_pattern_list or []
    if isinstance(pattern_list, basestring):
        pattern_list = [pattern_list,]
    expanded = []
    for pattern in pattern_list:
        if not isinstance(pattern, Path):
            pattern = Path(pattern)
        assert isinstance(pattern, Path)
        for item in pattern.glob():
            assert isinstance(item, Path)
            if item in expanded:
                continue
            skip = False
            for exclude_pattern in exclude_pattern_list:
                if not isinstance(exclude_pattern, Path):
                    exclude_pattern = Path(exclude_pattern)
                assert isinstance(exclude_pattern, Path)
                for exclude in exclude_pattern.glob():
                    if exclude.pathname == item.pathname:
                        skip = True
                        break
                    if exclude.exists and (exclude.samefile(item) or exclude.same(item)):
                        skip = True
                        break
            if skip:
                continue
            if item not in expanded:
                expanded.append(item)
    return expanded

class Application(object):
    """Application singleton."""

    _instance = None

    def __init__(self, opts, args, command):
        assert Application._instance is None
        Application._instance = self

        # -- member variables ----------------------------------------------------
        self.options = opts
        self.args    = args
        self.command = command
        self.olddir  = Path.Cwd()

        self.config         = None
        self.hosts          = None
        self.root           = None
        self.repositories   = None
        self.exclude        = None
        self.export         = None
        self.export_exclude = None
        self.sync           = None
        self.sync_exclude   = None

        self._setup_automa_logging()
        self._parse_config_file()

    def run(self):
        assert self.root
        cd(self.root)

        r = False
        if self.command in ('serve', 'server'):
            r = self.handle_serve()
        elif self.command in ('sync', 'synchronize',):
            r = self.handle_sync()
        else:
            error("unknown command '%s'" % self.command)
            r = False

        cd(self.olddir)
        if not r:
            sys.exit(1)
        return self

    def _setup_automa_logging(self):
        from automa.opts import _setup_default_options
        from automa.tasks import Task, TaskContext
    
        global options
    
        _setup_default_options()
    
        #logging.basicConfig(level=logging.DEBUG)
        level = cmdutils.log.Logger.DEBUG
        logger = cmdutils.log.Logger([(level, sys.stderr)])
        options.logger        = logger
        options.dry_run       = False
        options.ignore_errors = False
    
        def syncbzr():
            pass
        dummy_t = Task(syncbzr)
        dummy_tc = TaskContext(dummy_t)
        dummy_tc._logger = logger
        TaskContext._active_task_context = dummy_tc

    def _parse_config_file(self):
        fh = open(os.path.expanduser(str(self.options.config)), 'r')
        self.config = yaml.load(fh)
        fh.close()

        debug("config:%s" % repr(self.config))
        self.hosts          = self.config['hosts']
        self.root           = Path(os.path.expanduser(self.config['root']))
        self.repositories   = self.config['repositories']
        self.exclude        = self.config['exclude']
        self.export         = self.config['export']
        self.export_exclude = self.config['export_exclude']
        self.sync           = self.config['sync']
        self.sync_exclude   = self.config['sync_exclude']

        assert isinstance(self.hosts, (tuple, list))
        if this_host in self.hosts:
            self.hosts.remove(this_host)
    
        assert this_host not in self.hosts

    # ------------------------------------------------------------------------
    #   COMMANDS
    # ------------------------------------------------------------------------

    def handle_serve(self):
        """Run in server mode."""
        handler = AppHandler(self)
        app = jsonrpc2.JsonRpcApplication(rpcs=JsonRPCDispatcher(handler))
    
        server = wsgiserver.CherryPyWSGIServer((self.options.host, int(self.options.port)), app)
        info('Serving on http://%s:%s' % (self.options.host, self.options.port))
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
        return True

    def _sync_repo(self, host, port, repository):
        """
        Synchronize the specified repository from the remote node specified
        as (host, port).
        """
        if host == this_host:
            warn("Can't synchronize with itself!")
            return False
        if not isinstance(repository, Path):
            repository = Path(repository)
        assert isinstance(repository, Path)
        debug("repository:%s" % repository)
        if repository.isabs:
            repository = repository.relativeto(self.root)
            if repository.isabs:
                error("Only repositories inside '%s' are supported." % self.root)
                return False
        assert not repository.isabs

        abs_repository = repository.abspath
        assert isinstance(abs_repository, Path)
        assert abs_repository.same(self.root / repository)

        sync_exclude = expand_pattern_list(self.sync_exclude)
        sync         = expand_pattern_list(self.sync, sync_exclude)
        if repository in sync_exclude:
            error("requested an excluded repository.")
            return False
        if not repository in sync:
            error("requested repository is not among those specified in 'sync' option.")
            return False
        assert repository in sync

        # Fetch branches available on host under repo/HOST/
        proxy = JsonRpcProxy("http://%s:%s/" % (host, port))
        available_branches = proxy.exported_branches(this_host, str(repository))
        print available_branches

        # TODO: Filter out branches excluded by config file
        branches = available_branches
        if len(branches) == 0:
            return True
        info("Synchronizing repository '%s' from %r" % (repository, host))
        debug("sync branches %s" % ", ".join([b for b in branches]))
        for branch in branches:
            local_branch  = abs_repository / host / branch
            remote_branch = "%s/%s" % (host, branch)
            info("synchronizing %s" % local_branch)
            if not local_branch.exists:
                info("local branch not yet created. Initializing...")
                sh("bzr init %(dst)s", vars={'dst': local_branch})
            sh("bzr pull -d %(dst)s bzr://%(host)s/%(remoterepo)s/%(srcbranch)s", vars={'dst': local_branch,
                                                                                        'host': host,
                                                                                        'remoterepo': repository,
                                                                                        'srcbranch': remote_branch})
        return True

    def handle_sync(self):
        """
        Synchronize repositories specified on the command line from a remote node.
        If no repository is specified, then synchronize all repositories.
        """
        if self.options.host == this_host:
            warn("Can't synchronize with itself!")
            return False

        hosts = []
        if (not self.options.host) or (self.options.host == '') or (self.options.host == '0.0.0.0'):
            hosts = self.hosts
        else:
            hosts = ["%s:%s" % (self.options.host, self.options.port),]

        sync_exclude = expand_pattern_list(self.sync_exclude)
        sync         = expand_pattern_list(self.sync, sync_exclude)

        specified_repositories = list(self.args)
        if len(specified_repositories) < 1:
            # sync all repositories
            specified_repositories = sync

        repositories = []
        for repospec in specified_repositories:
            if repospec.startswith("set:"):
                set_name = repospec[4:]
                set_value = expand_pattern_list(self.config['set_%s' % set_name])
                repositories.extend(set_value)
            else:
                repositories.append(repospec)

        result = True
        for host_port in hosts:
            assert isinstance(host_port, basestring)
            if ':' in host_port:
                (host, port) = host_port.rsplit(':', 1)
            else:
                (host, port) = (host_port, self.options.port)
            if host == this_host:
                warn("Can't synchronize with itself. Skipping host '%s'" % host)
                result = False
                continue
            alive = ping(host)
            if not alive:
                info("Host %r doesn't appear to be online. Skipping..." % host)
                result = False
                continue
            info("Synchronizing from %s:%s" % (host, port))
            for repository in repositories:
                r = self._sync_repo(host, port, repository)
                result = result and r
        return result

class AppHandler(object):
    """JSON-RPC handler for the application."""

    def __init__(self, application):
        assert isinstance(application, Application)

        # -- member variables ----------------------------------------------------
        self.application = application

    # ------------------------------------------------------------------------
    #   JSON-RPC METHODS
    # ------------------------------------------------------------------------

    def exported_repositories(self, host):
        export_exclude = expand_pattern_list(self.application.export_exclude)
        export         = expand_pattern_list(self.application.export, export_exclude)
        exported = []
        for repo in export:
            assert isinstance(repo, Path)
            if repo.isabs:
                absrepo = repo
            else:
                absrepo = repo.abspath
            exported.append(absrepo.relativeto(self.application.root).pathname)
        return exported

    def exported_branches(self, host, repository):
        export_exclude = expand_pattern_list(self.application.export_exclude)
        export         = expand_pattern_list(self.application.export, export_exclude)
        if not isinstance(repository, Path):
            repository = Path(repository)
        assert isinstance(repository, Path)
        if repository.isabs:
            warn("absolute repositories are not allowed.")
            return []
        if repository in export_exclude:
            warn("requested an excluded repository.")
            return []
        if repository not in export:
            warn("requested repository is not present/exported.")
            return []
        assert repository in export
        if not repository.isabs:
            repository = self.application.root / repository
        assert isinstance(repository, Path)
        branches = get_branches(repository / this_host)
        return [str(b.relpath) for b in branches]

class JsonRPCDispatcher(object):
    def __init__(self, handler):
        self.handler = handler

    def __iter__(self):
        return iter(self.handler.__dict__)

    def __contains__(self, key):
        return hasattr(self.handler, key)

    def __getitem__(self, key):
        if hasattr(self.handler, key):
            return getattr(self.handler, key)
        raise KeyError(key)

class JsonRpcClientException(Exception):
    def __init__(self, data):
        self.data    = data
        self.error   = self.data['error']
        self.message = self.error['message']
        self.code    = self.error['code']

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<JsonRpcClientException '%s' code:%s>" % (self.message, self.code)

class JsonRpcProxy(object):
    class Method(object):
        def __init__(self, proxy, name, id=None):
            assert isinstance(proxy, JsonRpcProxy)
            self.proxy = proxy
            self.name  = name
            self.id    = id

        def __call__(self, *args, **kwargs):
            id = self.proxy._make_id(self)
            json_data = dict(jsonrpc = '2.0',
                             method  = self.name,
                             params  = list(args),
                             id      = id)
            json_encoded = json.dumps(json_data)
            request = urllib2.Request(self.proxy.url, json_encoded, {'Content-Type': "application/json"})
            response = urllib2.urlopen(request)
            result = response.read()
            if not result:
                return None
            result = json.loads(result)
            if not result:
                return None
            if result.has_key('error'):
                raise JsonRpcClientException(result)
            return result['result']

    ID_DOMAIN = "proxy"
    ID_CTR    = 0

    def __init__(self, url, domain=None):
        self.domain = domain or JsonRpcProxy.ID_DOMAIN
        self.url = url

    def __getattr__(self, name):
        # Note, even attributes like __contains__ can get routed
        # through __getattr__
        if name.startswith('_'):
            raise AttributeError(name)
        return self.Method(self, name)

    def _next_id(self):
        next_id = JsonRpcProxy.ID_CTR
        JsonRpcProxy.ID_CTR += 1
        return next_id

    def _make_id(self, method):
        assert isinstance(method, JsonRpcProxy.Method)
        id = method.id or self._next_id()
        return "%s-%s-%s" % (self.domain, method.name, id)

def main(args=None):
    import optparse
    parser = optparse.OptionParser(
        usage="%prog [OPTIONS] [COMMAND] [COMMAND-ARGUMENTS]")
    parser.add_option(
        '-p', '--port', default=DEFAULT_PORT,
        help='Port to serve on/connect to (default %s)' % DEFAULT_PORT)
    parser.add_option(
        '-H', '--host', default=DEFAULT_HOST,
        help='Host to serve on/connect to (default %s)' % DEFAULT_HOST)
    parser.add_option(
        '-c', '--config', default=DEFAULT_CONFIG,
        help='bzrsync YAML configuration file (default %s)' % DEFAULT_CONFIG)
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args()

    command = 'serve'
    if args and len(args) > 0:
        command = args[0]
        args = args[1:]

    application = Application(options, args, command)
    application.run()

if __name__ == '__main__':
    main()
