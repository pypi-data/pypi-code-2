from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery

jquery_lib = Library('jquery_lib', 'jquery-build')
jqueryutils_lib = Library('jqueryutils_lib', 'jqueryutils-build')

css = ResourceInclusion(jqueryutils_lib, 'jquery.utils.css')
jqueryutils = ResourceInclusion(jqueryutils_lib, 'jquery.utils.js', depends=[css, jquery], minified='jquery.utils.min.js')
