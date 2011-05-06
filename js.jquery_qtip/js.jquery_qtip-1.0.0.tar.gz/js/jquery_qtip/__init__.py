from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery.qtip', 'resources')

qtip_js = Resource(
    library,
    'jquery.qtip.js',
    minified='jquery.qtip.min.js',
    depends=[jquery]
)

qtip = qtip_js
