from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_qunit', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

jquery_qunit_css = Resource(library, 'qunit.css')
jquery_qunit = Resource(library, 'qunit.js', depends=[jquery_qunit_css, jquery])
