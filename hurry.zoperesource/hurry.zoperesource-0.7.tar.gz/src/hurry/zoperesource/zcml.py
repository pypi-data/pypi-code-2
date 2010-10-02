from zope.interface import Interface
from hurry import resource
from hurry.resource import zca
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.browserresource.directory import DirectoryResourceFactory
from zope.security.checker import NamesChecker

class ISetupHurryZopeResource(Interface):
    pass

allowed_resource_names = (
    'GET', 'HEAD', 'publishTraverse', 'browserDefault', 'request', '__call__')

allowed_resourcedir_names = allowed_resource_names + ('__getitem__', 'get')

def action_setup(_context):
    """Publish all hurry.resource library entry points as resources.
    """
    resource.register_plugin(zca.Plugin())

    for library in resource.libraries():
        checker = NamesChecker(allowed_resourcedir_names)
        resource_factory = DirectoryResourceFactory(
            library.path, checker, library.name)

        adapts = (IBrowserRequest,)
        provides = Interface

        _context.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (resource_factory, adapts, provides, library.name))

