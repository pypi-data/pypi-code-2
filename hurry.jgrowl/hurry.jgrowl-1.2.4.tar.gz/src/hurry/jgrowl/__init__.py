from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery

jgrowl_lib = Library('jgrowl_lib', 'jgrowl-build')

jgrowl_css = ResourceInclusion(jgrowl_lib, 'jquery.jgrowl.css')

jgrowl = ResourceInclusion(jgrowl_lib, 'jquery.jgrowl.js',
                           minified='jgrowl_minimized.js', 
                           depends=[jquery, jgrowl_css])
