from fanstatic import Library, Resource
from js.jquery import jquery
from js.jquery_metadata import metadata

library = Library('jquery_tablesorter', 'resources')

tablesorter = Resource(library, 'jquery.tablesorter.js',
    minified='jquery.tablesorter.min.js', depends=[jquery, metadata])

blue = Resource(library, 'themes/blue/style.css')

green = Resource(library, 'themes/green/style.css')

