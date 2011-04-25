from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_jstree', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')


# XXX: Separate eggs for these 2
jquery_hotkeys = Resource(
    library, '_lib/jquery.hotkeys.js',
    depends=[jquery])
jquery_cookie = Resource(
    library, '_lib/jquery.cookie.js',
    depends=[jquery])

# XXX minified version would be nice
jquery_jstree = Resource(
    library, 'jquery.jstree.js',
    depends=[jquery, jquery_hotkeys, jquery_cookie])

