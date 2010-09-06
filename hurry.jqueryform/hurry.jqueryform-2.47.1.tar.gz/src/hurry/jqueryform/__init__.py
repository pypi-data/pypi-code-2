from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery

jqueryform_lib = Library('jqueryform', 'jqueryform-build')

jqueryform = ResourceInclusion(
    jqueryform_lib, 'jquery.form.js',
    depends=[jquery],
    minified='jquery.form.min.js')
