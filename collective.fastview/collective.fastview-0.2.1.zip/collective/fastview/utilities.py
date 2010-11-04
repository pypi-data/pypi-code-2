"""

    Misc. view helpers.
    
    http://mfabrik.com

"""

__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__copyright__ = "2010 mFabrik Research Oy"
__docformat__ = "epytext"
__license__ = "GPL 2"

import os
import sys

from five import grok
from grokcore.view.components import PageTemplateFile

def fix_grok_template_inheritance(klass, another):
    """
    This fixes grok 1.0 problem that view and viewlets template are not inheritable between packages.
    E.g. if you subclass a view you need to manually copy over the view template also.
    
    We hope to get rid of this with Plone 4 / fixed grok.
    
    See:
    
    * https://bugs.launchpad.net/grok/+bug/255005
    """
    
    template = getattr(klass, "grokcore.view.directive.template", None)
    if template == None:
        # Get template using grok mechanism
        template = another.__name__.lower()
            
    
    module = another.__module__
    
    desc = sys.modules[module]
    
    dirname = os.path.dirname(desc.__file__)
    
    templatedir = os.path.join(dirname, "templates")

    template_file = template + ".pt"
    template = os.path.join(templatedir, template_file)
    
    klass.template = PageTemplateFile(filename=template_file, _prefix=templatedir)
    
    