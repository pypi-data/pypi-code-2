from fanstatic import Library, Resource, GroupResource
from js.jquery import jquery

library = Library('jquery_slimbox', 'resources')

slimbox_css = Resource(library, 'css/slimbox2.css')

slimbox_js = Resource(library, 'js/slimbox2.js', depends=[jquery])

slimbox = GroupResource([slimbox_css, slimbox_js])
