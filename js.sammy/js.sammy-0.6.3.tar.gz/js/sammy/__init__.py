from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('sammy.js', 'resources')

sammy_js = Resource(
    library,
    'sammy.js',
    minified='sammy.min.js',
    depends=[jquery]
)

sammy = sammy_js
