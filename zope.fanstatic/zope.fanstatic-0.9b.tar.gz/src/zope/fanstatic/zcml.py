from zope.interface import Interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest

import fanstatic

from zope.fanstatic.zopesupport import ZopeFanstaticResource

def create_factory(library):
    def factory(request):
        return ZopeFanstaticResource(request, library)
    return factory

def action_setup(_context):
    """Publish all fanstatic library entry points as resources.
    """
    for library in fanstatic.get_library_registry().values():
        factory = create_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface
        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (factory, adapts, provides, library.name))

