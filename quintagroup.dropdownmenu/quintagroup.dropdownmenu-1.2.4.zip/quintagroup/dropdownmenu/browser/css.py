import os

from Products.Five.browser import BrowserView


class CSSHoverView(BrowserView):
    """Return csshover.htc js for IE < 7, this requires python class only
    because of need to set custom content type for that resource.
    """

    def __call__(self):
        """Main method"""
        resource = file(os.path.join(os.path.dirname(__file__),
                                     'resources', 'csshover.htc'), 'r').read()
        self.request.response.setHeader('Content-Type', 'text/x-component')
        return resource
