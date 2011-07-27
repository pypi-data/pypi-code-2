# This recipe currently does ``nothing``[1][2][3][4] except require Bluebream packages.
# In the future, it may do ``something``.

# [1] Actually, it installs ``bin/paster``
# [2] And it includes a small WSGI application
# [3] And some ZCML files.
# [4] And it creates ``var/{filestorage, blobstorage}`` if they do not exist

from zc.buildout.easy_install import scripts
import os, pkg_resources
import logging

logger = logging.getLogger('collective.recipe.bluebream')

def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        print '%s exists' % dir

class Recipe(object):
    
    def __init__(self, buildout, name, options):
        self.buildout = buildout

    def install(self):

        # Create var dirs
        var = os.path.join(self.buildout['buildout']['directory'], 'var')
        fs = os.path.join(self.buildout['buildout']['directory'], 'var', 'filestorage')
        bs = os.path.join(self.buildout['buildout']['directory'], 'var', 'blobstorage')
        mkdir(var)
        mkdir(fs)
        mkdir(bs)

        # Generate paster script
        return scripts(['PasteScript'], pkg_resources.working_set,
            self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'])


    def update(self):
        pass

import zope.app.wsgi

def application_factory(global_conf):
    zope_conf = global_conf['zope_conf']
    return zope.app.wsgi.getWSGIApplication(zope_conf)
