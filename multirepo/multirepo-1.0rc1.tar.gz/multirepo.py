#!/usr/bin/python

"""affect multiple repositories simultaneously

All commands that affect other repositories (push, paths, out and bundle) are
wrapped.

Add paths to target to .hgrc in the [multirepo] section; attributes
starting with "path." are interpreted as targets for multirepo:

	[multirepo]
	path.abc = /path/to/a/repo
	path.another = /path/to/another/repo

The "default" path (or "default-push" if it is defined) is included in the
list of paths to this extension will target unless you set "include.default"
to False:

	[multirepo]
	include.default = False
	path.abc = /path/to/a/repo
	path.another = /path/to/another/repo

All wrapped commands affect all targets unless a specific target is given on the
command-line.
"""

import os
from mercurial import commands, cmdutil, extensions, patch

def new_paths(orig_paths, ui, repo, *pats, **opts):
	orig_paths(ui, repo, *pats, **opts)
	ui.write('\n'.join(['%s = %s' % x for x in ui.configitems('multirepo') if x[0].startswith('path')]))
	ui.write('\n')

def multiwrapper(orig, ui, repo, *pats, **opts):
	if pats:
		return orig(ui, repo, *pats, **opts)

	repos = [x[1] for x in ui.configitems('multirepo') if x[0].startswith('path')]

	def worker(p):
		p = os.path.expanduser(p)
		orig(ui, repo, p, **opts)
		ui.status('\n')
	
	if ui.config('multirepo', 'include.default', True):
		worker(ui.config('paths', 'default-push', ui.config('paths', 'default', 'DEFAULT')))
	
	for p in repos:
		worker(p)	

def new_bundle(orig, ui, repo, filename, *dest, **opts):
	if dest:
		return orig(ui, repo, filename, *dest, **opts)
	
	repos = [x for x in ui.configitems('multirepo') if x[0].startswith('path')]
	i = iter(range(200))
	
	def worker(pname, p):
		ui.status('comparing with %s\n' % p)
		fname = filename + (('_' + pname[len('path.'):]) if pname != 'default' else '')
		p = os.path.expanduser(p)
		orig(ui, repo, fname , p, **opts)
		ui.note('changesets bundled and stored in %s\n' % fname)
		ui.write('\n')
		
	if ui.config('multirepo', 'include.default', True):
		worker('default', ui.config('paths', 'default-push', ui.config('paths', 'default', 'DEFAULT')))
	
	for pname, p in repos:
		worker(pname, p)

def uisetup(ui):
    if not hasattr(extensions, 'wrapcommand'):
        return # doesn't work as nicely on old hg versions
    extensions.wrapcommand(commands.table, 'bundle', new_bundle)
    extensions.wrapcommand(commands.table, 'out', multiwrapper)
    extensions.wrapcommand(commands.table, 'push', multiwrapper)
    extensions.wrapcommand(commands.table, 'paths', new_paths)
