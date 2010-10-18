from hurry.resource import Library, ResourceInclusion

jquery_lib = Library('jquery_lib', 'jquery-build')

jquery = ResourceInclusion(jquery_lib, 'jquery-1.4.3.js', minified='jquery-1.4.3.min.js')