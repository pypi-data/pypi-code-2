import os
from types import TupleType

from zope.interface import implements
from zope import component

from hurry.resource import interfaces

EXTENSIONS = ['.css', '.kss', '.js']

class Library(object):
    implements(interfaces.ILibrary)
    
    def __init__(self, name):
        self.name = name

class ResourceInclusion(object):
    """Resource inclusion
    
    A resource inclusion specifies how to include a single resource in
    a library.
    """
    implements(interfaces.IResourceInclusion)
    
    def __init__(self, library, relpath, depends=None,
                 supersedes=None, eager_superseder=False,
                 bottom=False, **kw):
        """Create a resource inclusion

        library  - the library this resource is in
        relpath  - the relative path from the root of the library indicating
                   the actual resource
        depends  - optionally, a list of resources that this resource depends
                   on. Entries in the list can be
                   ResourceInclusions or strings indicating the path.
                   In case of a string, a ResourceInclusion assumed based
                   on the same library as this inclusion.
        supersedes - optionally, a list of resources that this resource
                   supersedes as a rollup resource. If all these
                   resources are required, the superseding resource
                   instead will show up.
        eager_superseder - even if only part of the requirements are
                           met, supersede anyway
        bottom - optionally, indicate that this resource can be
                 safely included on the bottom of the page (just
                 before ``</body>``). This can be used to
                 improve the performance of page loads when javascript
                 resources are in use. Not all javascript-based resources
                 can however be safely included that way.
        keyword arguments - different paths that represent the same
                  resource in different modes (debug, minified, etc),
                  or alternatively a fully specified ResourceInclusion.
        """
        self.library = library
        self.relpath = relpath
        self.bottom = bottom
        
        assert not isinstance(depends, basestring)
        depends = depends or []
        self.depends = normalize_inclusions(library, depends)
        
        self.rollups = []

        normalized_modes = {}
        for mode_name, inclusion in kw.items():
            normalized_modes[mode_name] = normalize_inclusion(
                library, inclusion)
        self.modes = normalized_modes
 
        assert not isinstance(supersedes, basestring)
        self.supersedes = supersedes or []
        self.eager_superseder = eager_superseder
        
        # create a reference to the superseder in the superseded inclusion
        for inclusion in self.supersedes:
            inclusion.rollups.append(self)
        # also create a reference to the superseding mode in the superseded
        # mode
        # XXX what if mode is full-fledged resource inclusion which lists
        # supersedes itself?
        for mode_name, mode in self.modes.items():
            for inclusion in self.supersedes:
                superseded_mode = inclusion.mode(mode_name)
                # if there is no such mode, let's skip it
                if superseded_mode is inclusion:
                    continue
                mode.supersedes.append(superseded_mode)
                superseded_mode.rollups.append(mode)
    
    def __repr__(self):
        return "<ResourceInclusion '%s' in library '%s'>" % (
            self.relpath, self.library.name)

    def ext(self):
        name, ext = os.path.splitext(self.relpath)
        return ext

    def mode(self, mode):
        if mode is None:
            return self
        # try getting the alternative
        try:
            return self.modes[mode]
        except KeyError:
            # fall back on the default mode if mode not found
            return self
    
    def key(self):
        return self.library.name, self.relpath

    def need(self):
        needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
        needed.need(self)

    def inclusions(self):
        """Get all inclusions needed by this inclusion, including itself.
        """
        result = []
        for depend in self.depends:
            result.extend(depend.inclusions())
        result.append(self)
        return result

class GroupInclusion(object):
    """An inclusion used to group resources together.

    It doesn't define a resource itself.
    """
    implements(interfaces.IInclusion)

    def __init__(self, depends):
        self.depends = depends

    def need(self):
        needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
        needed.need(self)

    def inclusions(self):
        """Get all inclusions needed by this inclusion.
        """
        result = []
        for depend in self.depends:
            result.extend(depend.inclusions())
        return result

def normalize_inclusions(library, inclusions):
    return [normalize_inclusion(library, inclusion)
            for inclusion in inclusions]

def normalize_inclusion(library, inclusion):
    if interfaces.IInclusion.providedBy(inclusion):
        return inclusion
    assert isinstance(inclusion, basestring)
    return ResourceInclusion(library, inclusion)

class NeededInclusions(object):
    def __init__(self):
        self._inclusions = []
        self._mode = None
        self._rollup = False
        self._bottom = False
        self._force_bottom = False
        
    def need(self, inclusion):
        self._inclusions.append(inclusion)

    def mode(self, mode):
        self._mode = mode

    def bottom(self, force=False, disable=False):
        if disable:
            self._bottom = False
            self._force_bottom = False
            return
        self._bottom = True
        if force:
            self._force_bottom = True

    def rollup(self, disable=False):
        if disable:
            self._rollup = False
        self._rollup = True
        
    def _sorted_inclusions(self):
        return reversed(sorted(self._inclusions, key=lambda i: i.depth()))
    
    def inclusions(self):
        inclusions = []
        for inclusion in self._inclusions:
            inclusions.extend(inclusion.inclusions())

        inclusions = apply_mode(inclusions, self._mode)
        if self._rollup:
            inclusions = consolidate(inclusions)
        # sort only by extension, not dependency, as we can rely on
        # python's stable sort to keep inclusion order intact
        inclusions = sort_inclusions_by_extension(inclusions)
        inclusions = remove_duplicates(inclusions)
        
        return inclusions

    def render(self):
        return render_inclusions(self.inclusions())

    def render_into_html(self, html):
        to_insert = self.render()
        return html.replace('<head>', '<head>\n    %s\n' % to_insert, 1)
        
    def render_topbottom(self):
        inclusions = self.inclusions()

        # seperate inclusions in top and bottom inclusions if this is needed
        if self._bottom:
            top_inclusions = []
            bottom_inclusions = []
            if not self._force_bottom:
                for inclusion in inclusions:
                    if inclusion.bottom:
                        bottom_inclusions.append(inclusion)
                    else:
                        top_inclusions.append(inclusion)
            else:
                for inclusion in inclusions:
                    if inclusion.ext() == '.js':
                        bottom_inclusions.append(inclusion)
                    else:
                        top_inclusions.append(inclusion)
        else:
            top_inclusions = inclusions
            bottom_inclusions = []

        library_urls = {}
        return (render_inclusions(top_inclusions, library_urls),
                render_inclusions(bottom_inclusions, library_urls))

    def render_topbottom_into_html(self, html):
        top, bottom = self.render_topbottom()
        if top:
            html = html.replace('<head>', '<head>\n    %s\n' % top, 1)
        if bottom:
            html = html.replace('</body>', '%s</body>' % bottom, 1)
        return html

def mode(mode):
    """Set the mode for the currently needed resources.
    """
    needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
    needed.mode(mode)

def bottom(force=False, disable=False):
    """Try to include resources at the bottom of the page, not just on top.
    """
    needed = component.getUtility(
            interfaces.ICurrentNeededInclusions)()
    needed.bottom(force, disable)

def rollup(disable=False):
    needed = component.getUtility(
        interfaces.ICurrentNeededInclusions)()
    needed.rollup(disable)

def render():
    needed = component.getUtility(
        interfaces.ICurrentNeededInclusions)()
    return needed.render()

def render_into_html(html):
    needed = component.getUtility(
        interfaces.ICurrentNeededInclusions)()
    return needed.render_into_html(html)

def render_topbottom():
    needed = component.getUtility(
        interfaces.ICurrentNeededInclusions)()
    return needed.render_topbottom()

def render_topbottom_into_html(html):
    needed = component.getUtility(
        interfaces.ICurrentNeededInclusions)()
    return needed.render_topbottom_into_html(html)

def apply_mode(inclusions, mode):
    return [inclusion.mode(mode) for inclusion in inclusions]

def remove_duplicates(inclusions):
    """Given a set of inclusions, consolidate them so each only occurs once.
    """
    seen = set()
    result = []
    for inclusion in inclusions:
        if inclusion.key() in seen:
            continue
        seen.add(inclusion.key())
        result.append(inclusion)
    return result

def consolidate(inclusions):
    # keep track of rollups: rollup key -> set of inclusion keys
    potential_rollups = {}
    for inclusion in inclusions:
        for rollup in inclusion.rollups:
            s = potential_rollups.setdefault(rollup.key(), set())
            s.add(inclusion.key())

    # now go through inclusions, replacing them with rollups if
    # conditions match
    result = []
    for inclusion in inclusions:
        eager_superseders = []
        exact_superseders = []
        for rollup in inclusion.rollups:
            s = potential_rollups[rollup.key()]
            if rollup.eager_superseder:
                eager_superseders.append(rollup)
            if len(s) == len(rollup.supersedes):
                exact_superseders.append(rollup)
        if eager_superseders:
            # use the eager superseder that rolls up the most
            eager_superseders = sorted(eager_superseders,
                                       key=lambda i: len(i.supersedes))
            result.append(eager_superseders[-1])
        elif exact_superseders:
            # use the exact superseder that rolls up the most
            exact_superseders = sorted(exact_superseders,
                                       key=lambda i: len(i.supersedes))
            result.append(exact_superseders[-1])
        else:
            # nothing to supersede resource so use it directly
            result.append(inclusion)                
    return result

def sort_inclusions_by_extension(inclusions):

    def key(inclusion):
        return EXTENSIONS.index(inclusion.ext())

    return sorted(inclusions, key=key)

def sort_inclusions_topological(inclusions):
    """Sort inclusions by dependency and supersedes.
    """
    dead = {}
    result = []
    for inclusion in inclusions:
        dead[inclusion.key()] = False

    for inclusion in inclusions:
        _visit(inclusion, result, dead)
    return result

def _visit(inclusion, result, dead):
    if dead[inclusion.key()]:
        return
    dead[inclusion.key()] = True
    for depend in inclusion.depends:
        _visit(depend, result, dead)
    for depend in inclusion.supersedes:
        _visit(depend ,result, dead)
    result.append(inclusion)

def render_css(url):
    return ('<link rel="stylesheet" type="text/css" href="%s" />' %
            url)

def render_kss(url):
    raise NotImplementedError

def render_js(url):
    return ('<script type="text/javascript" src="%s"></script>' %
            url)

inclusion_renderers = {
    '.css': render_css,
    '.kss': render_kss,
    '.js': render_js,
    }

def render_inclusions(inclusions, library_urls=None):
    """Render a set of inclusions.

    inclusions - the inclusions to render
    library_urls - optionally a dictionary for maintaining cached library
                   URLs. Doing render_inclusions with the same
                   dictionary can reduce component lookups.
    """
    result = []
    library_urls = library_urls or {}
    for inclusion in inclusions:
        library = inclusion.library
        # get cached library url
        library_url = library_urls.get(library.name)
        if library_url is None:
            # if we can't find it, recalculate it
            library_url = interfaces.ILibraryUrl(library)
            if not library_url.endswith('/'):
                library_url += '/'
            library_urls[library.name] = library_url
        result.append(render_inclusion(inclusion,
                                       library_url + inclusion.relpath))
    return '\n'.join(result)

def render_inclusion(inclusion, url):
    renderer = inclusion_renderers.get(inclusion.ext(), None)
    if renderer is None:
        raise interfaces.UnknownResourceExtension(
            "Unknown resource extension %s for resource inclusion: %s" %
            (inclusion.ext(), repr(inclusion)))
    return renderer(url)

def generate_code(**kw):
    name_to_inclusion = kw
    inclusion_to_name = {}
    inclusions = []
    for name, inclusion in kw.items():
        inclusion_to_name[inclusion.key()] = name
        inclusions.append(inclusion)
        
    # libraries with the same name are the same libraries
    libraries = {}
    for inclusion in inclusions:
        libraries[inclusion.library.name] = inclusion.library
    libraries = sorted(libraries.values())

    result = []
    # import on top
    result.append("from hurry.resource import Library, ResourceInclusion")
    result.append("")
    # define libraries
    for library in libraries:
        result.append("%s = Library('%s')" % (library.name, library.name))
    result.append("")

    # sort inclusions in the order we want them to be
    inclusions = sort_inclusions_by_extension(
        sort_inclusions_topological(inclusions))
 
    # now generate inclusion code
    for inclusion in inclusions:
        s = "%s = ResourceInclusion(%s, '%s'" % (
            inclusion_to_name[inclusion.key()],
            inclusion.library.name,
            inclusion.relpath)
        if inclusion.depends:
            depends_s = ', depends=[%s]' % ', '.join(
                [inclusion_to_name[d.key()] for d in inclusion.depends])
            s += depends_s
        if inclusion.supersedes:
            supersedes_s = ', supersedes=[%s]' % ', '.join(
                [inclusion_to_name[i.key()] for i in inclusion.supersedes])
            s += supersedes_s
        if inclusion.modes:
            items = []
            for mode_name, mode in inclusion.modes.items():
                items.append((mode_name,
                              generate_inline_inclusion(mode, inclusion)))
            items = sorted(items)
            modes_s = ', %s' % ', '.join(["%s=%s" % (name, mode) for
                                          (name, mode) in items])
            s += modes_s
        s += ')'
        result.append(s)
    return '\n'.join(result)

def generate_inline_inclusion(inclusion, associated_inclusion):
    if inclusion.library.name == associated_inclusion.library.name:
        return "'%s'" % inclusion.relpath
    else:
        return "ResourceInclusion(%s, '%s')" % (inclusion.library.name,
                                                inclusion.relpath)
    
