from fanstatic import Library, Resource

from js.jquery import jquery

library = Library('jquery_tooltip', 'resources')

jquery_tooltip_css = Resource(library, 'jquery.tooltip.css')

jquery_tooltip = Resource(library, 'jquery.tooltip.js',
    minified='jquery.tooltip.min.js',
    depends=[jquery, jquery_tooltip_css])

