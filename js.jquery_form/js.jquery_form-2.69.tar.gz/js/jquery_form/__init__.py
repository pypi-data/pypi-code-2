from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_form', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

jquery_form = Resource(
    library,
    'jquery.form.js',
    depends=[jquery]
)
