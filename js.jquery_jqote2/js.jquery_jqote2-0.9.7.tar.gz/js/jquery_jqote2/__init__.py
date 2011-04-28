from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery.jqote2', 'resources')

jqote2_js = Resource(
    library, 
    'jquery.jqote2.js',
    minified='jquery.jqote2.min.js',
    depends=[jquery]
)
jqote2 = jqote2_js
