from cStringIO import StringIO

from Products.HSCustom.Extensions.utils import *
from Products.HSCustom.config import *

def install(self):
    out = StringIO()

    setupSkins(self, out, GLOBALS, SKINSELECTIONS, SELECTSKIN, DEFAULTSKIN,
                          ALLOWSELECTION, PERSISTENTCOOKIE)
    registerStylesheets(self, out, STYLESHEETS)
    registerScripts(self, out, JAVASCRIPTS)

    print >> out, "Installation completed."
    return out.getvalue()

def uninstall(self):
    out = StringIO()

    removeSkins(self, out, SKINSELECTIONS, DEFAULTSKIN, RESETSKINTOOL)
    resetCSSResources(self, out, STYLESHEETS)
