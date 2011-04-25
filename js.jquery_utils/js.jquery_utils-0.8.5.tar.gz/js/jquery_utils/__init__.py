from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_utils', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

jquery_utils_css = Resource(library, 'jquery.utils.css')

jquery_utils = Resource(library, 'jquery.utils.js', depends=[jquery_utils_css, jquery],
                                minified='jquery.utils.min.js')

jquery_ddbelatedpng = Resource(library, 'jquery.ddbelated.js',
                        depends=[jquery],
                        minified='jquery.ddbelated.min.js')
