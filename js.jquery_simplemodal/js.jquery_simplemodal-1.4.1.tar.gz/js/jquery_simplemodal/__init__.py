from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery.simplemodal', 'resources')

jquery_simplemodal_js = Resource(
    library, 
    'jquery.simplemodal.js',
    minified='jquery.simplemodal.min.js',
    depends=[jquery]
)
jquery_simplemodal = jquery_simplemodal_js
