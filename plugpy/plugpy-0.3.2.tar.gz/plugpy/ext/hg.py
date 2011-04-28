import os.path
from cStringIO import StringIO

from plugpy import *

from mercurial import cmdutil, patch

class MercurialPlugin(object):

    def __init__(self, *args, **kwargs):
        pass

    def get_patch(self, repo, ui, changeset):
        revs = cmdutil.revrange(repo, [changeset])
        fp = StringIO()
        patch.export(repo, revs, template=fp,
                     switch_parent=None,
                 opts=patch.diffopts(ui, {}))
        return fp.getvalue()

loaded = False

def hook(hooktype, *args, **kwargs):
    config = dict()
    global loaded
    if not loaded:
        path = os.path.join(kwargs['repo'].root, './.hghooks')
        res = load_plugins(config, plugin_path=path, plugin_class=[MercurialPlugin],
                debug=False)
        loaded = True
    name = kwargs['repo'].dirstate.branch()
    results = dispatch(hooktype, *args, target=MercurialPlugin, branch_name=name, **kwargs)
    for res in results:
        if res[0]:
            return True
    return False

