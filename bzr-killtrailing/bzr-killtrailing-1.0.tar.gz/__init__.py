'''start_commit hook to strip trailing whitespaces from files
'''

import re

from bzrlib import mutabletree

version_info = 1,0

TRAILING = re.compile('\s+\n')


def fix(tree, fid):
    f = tree.get_file(fid)
    text = TRAILING.sub('\n', f.read().strip() + '\n')
    f.close()
    tree.put_file_bytes_non_atomic(fid, text)


def fixable(fn):
    return '.' in fn and fn.rsplit('.', 1)[1] in 'py js html css'


def strip_trailing_hook(tree):
    if not tree.has_changes():
        return
    changes = tree.changes_from(tree.basis_tree())

    for fn, fid, kind in changes.added:
        if fixable(fn):
            fix(tree, fid)

    for fn, fid, kind, changecount, _ in changes.modified:
        if changecount and fixable(fn):
            fix(tree, fid)

    for oldfn, fn, fid, kind, changecount, _ in changes.renamed:
        if changecount and fixable(fn):
            fix(tree, fid)


def install_hook(mod, hook, func, name):
    try:
        mod.hooks.install_named_hook(hook, func, name)
    except AttributeError:
        mod.hooks.install_hook(hook, func)
        mod.hooks.name_hook(func, name)


install_hook(mutabletree.MutableTree, 'start_commit',
             strip_trailing_hook, 'Strip trailing whitespaces')
