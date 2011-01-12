from Products.Five.browser.metaconfigure import IFiveViewDirective
from Products.Five.browser.metaconfigure import view
from zope.configuration.fields import Path
from gw2oe.forms.xml.factory import XMLFormFactory
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import os


class IFormViewDirective(IFiveViewDirective):

   template = Path(
        title=u"Form XML definition",
        description=u"""Form (XML) to use""",
        required=True
        )


class formview(view):

    def __init__(self, _context, for_, permission,
                 name='', layer=IDefaultBrowserLayer, class_=None,
                 allowed_interface=None, allowed_attributes=None,
                 menu=None, title=None, provides=Interface,
                 ):

        view.__init__(_context, for_, permission,
                      name=name, layer=IDefaultBrowserLayer, class_=class_,
                      allowed_interface=allowed_interface, 
                      allowed_attributes=allowed_attributes,
                      menu=menu, title=title, provides=Interface,
                      )

        if form:
            form = os.path.abspath(_context.path(form))
            if not os.path.isfile(form):
                raise ConfigurationError("No such file", form)
        else:
            raise ConfigurationError("Must specify a form")    

        xmlff = XMLFormFactory(xml)
        form = xmlff.createForm()

        _context.form = form
