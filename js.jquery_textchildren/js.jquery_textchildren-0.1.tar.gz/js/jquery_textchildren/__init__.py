from fanstatic import Library, Resource
import js.jquery

library = Library('jquery_textchildren', 'resources')

textchildren = Resource(library, 'jquery.textchildren.js',
    depends=[js.jquery.jquery])
