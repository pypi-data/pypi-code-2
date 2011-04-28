from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery.expandbox', 'resources')

expandbox_js = Resource(library, 'jquery.expandBox.js', depends=[jquery])
expandbox = expandbox_js
