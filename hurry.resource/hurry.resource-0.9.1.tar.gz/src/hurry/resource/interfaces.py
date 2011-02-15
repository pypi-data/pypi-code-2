from zope.interface import Interface, Attribute

class ILibrary(Interface):
    """A library contains one or more resources.

    A library has a unique name. It is expected to have multiple
    subclasses of the library class for particular kinds of resource
    libraries.
    """
    name = Attribute("The unique name of the library")

class IInclusion(Interface):
    """Base to all inclusions.
    """
    depends = Attribute("A list of inclusions that this "
                        "resource depends on")
    
    def need():
        """Express need directly for the current INeededInclusions.

        This is a convenience method to help express inclusions more
        easily, just do myinclusion.need() to have it be included in
        the HTML that is currently being rendered.
        """

    def inclusions():
        """Get all inclusions needed by this inclusion.
        """

class IResourceInclusion(IInclusion):
    """Resource inclusion

    A resource inclusion specifies how to include a single resource in a
    library.
    """
    library = Attribute("The resource library this resource is in")
    relpath = Attribute("The relative path of the resource "
                        "within the resource library")
    rollups = Attribute("A list of potential rollup ResourceInclusions "
                        "that this resource is part of")
    bottom = Attribute("A flag. When set to True, this resource "
                       "can be safely included on the bottom of a HTML "
                       "page, just before the </body> tag.")
    
    def ext():
        """Get the filesystem extension of this resource.

        This is used to determine what kind of resource we are dealing
        with.
        """

    def mode(mode):
        """Get the resource inclusion in a different mode.

        mode - the mode (minified, debug, etc) that we want this
               resource to be in. None is the default mode, and is
               this resource spec itself.

        An IResourceInclusion for that mode is returned.
        
        If we cannot find a particular mode for a resource, the
        original resource inclusion is returned.
        """

    def key():
        """Returns a unique, hashable identifier for the resource inclusion.
        """

class INeededInclusions(Interface):
    """A collection of inclusions that are needed for page display.
    """

    def need(inclusion):
        """Add the inclusion to the list of needed inclusions.

        See also IInclusion.need() for a convenience method.
        """

    def mode(mode):
        """Set the mode in which needed inclusions will be returned.

        try to put inclusions returned by ``render`` and
        ``inclusions`` into a particular mode (such as debug,
        minified, etc) Has no effect if an included resource does not
        know about that mode; the original resource will be included.

        The default mode is None; it is suggested this is the
        non-compressed/minified version of the Javascript/CSS to make
        debugging easier.
        
        Some suggested modes to use generally are 'debug' and 'minified'.
        'debug' is for full-source versions of the code so that it is
        easy to debug, while 'minified' is 
        
        mode - a string indicating the mode, or None if no mode.

        NOTE: there is also a ``hurry.resource.mode`` function which
        can be used to set the mode for the currently needed inclusions.
        """

    def bottom(force=False, disable=False):
        """Control the behavior of ``render_topbottom``.

        If not called or called with ``disable`` set to ``True``,
        resources will only be included in the top fragment returned
        by ``render_topbottom``.

        If called without arguments, resource inclusions marked safe
        to render at the bottom are rendered in the bottom fragment returned
        by ``render_topbottom``.

        If called with the ``force`` argument set to ``True``, Javascript
        (``.js``) resource inclusions are always included at the bottom.

        NOTE: there is also a ``hurry.resource.mode`` function which
        can be used to set the mode for the currently needed inclusions.
        """

    def rollup(disable=False):
        """Enable rolling up of resources.

        If not called or called with disable set to ``True``,
        resources are never consolidated into rollups.

        If called, resources will be consolidated into rollups if possible.
        """

    def inclusions():
        """Give all resource inclusions needed.

        Returns a list of resource inclusions needed.
        """

    def render():
        """Render all resource inclusions for HTML header.

        Returns a single HTML snippet to be included in the HTML
        page just after the ``<head>`` tag.

        ``force_bottom`` settings are ignored; everything is always
        rendered on top.
        """

    def render_into_html(html):
        """Render all resource inclusions into HTML.

        The HTML supplied needs to a <head> tag available. The
        inclusions HTML snippet will be rendered just after this.

        ``force_bottom`` settings are ignored; everything is always
        rendered on top.
        """

    def render_topbottom():
        """Render all resource inclusions into top and bottom snippet.

        Returns two HTML snippets that include the required resource
        inclusions, one for the top of the page, one for the bottom.

        if ``bottom`` was not called, behavior is like ``render``;
        only the top fragment will ever contain things to include, the
        bottom fragment will be empty.
        
        if ``bottom`` was called, bottom will include all resource
        inclusions that have ``bottom`` set to True (safe to include
        at the bottom of the HTML page), top will contain the rest.

        if ``bottom`` was called with the ``force`` argument set to
        ``True``, both top and bottom snippet will return content. top
        will contain all non-javascript resources, and bottom all
        javascript resources.

        The bottom fragment can be used to speed up page rendering:

        http://developer.yahoo.com/performance/rules.html
        
        Returns top and bottom HTML fragments.
        """

    def render_topbottom_into_html(html):
        """Render all resource inclusions into HTML (top and bottom).

        The HTML supplied needs to a <head> tag available. The
        top inclusions HTML snippet will be rendered just after this.

        The HTML supplied also needs to have a </body> tag available.
        bottom inclusions HTML snippet will be rendered just before this.
        """

class ICurrentNeededInclusions(Interface):
    def __call__():
        """Return the current needed inclusions object.

        These can for instance be retrieved from the current request.
        """

class ILibraryUrl(Interface):
    def __call__(inclusion):
        """Return the URL for the library.

        This is the URL that we can add inclusion.rel_path to, to obtain
        the complete URL of the resource.
        """

class UnknownResourceExtension(Exception):
    """Unknown resource extension"""
