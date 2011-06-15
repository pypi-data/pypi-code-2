from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.ProtectedFile.config import PROJECTNAME, GLOBALS
from StringIO import StringIO

def install(self):
    out = StringIO()

    classes = listTypes(PROJECTNAME)
    installTypes(self, out, classes, PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    print >> out, 'Successfully installed %s' % PROJECTNAME
    return out.getvalue()
