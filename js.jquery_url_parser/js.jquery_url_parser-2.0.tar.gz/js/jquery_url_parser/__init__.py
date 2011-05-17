from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery-url-parser', 'resources')

url_parser_js = Resource(
    library, 
    'jquery.url.js',
    depends=[jquery]
)
url_parser = url_parser_js
