from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

jquerytools_lib = Library('JqueryToolsLibrary', 'jquerytools-build')

jquerytools = ResourceInclusion(
    jquerytools_lib, 'jquery.tools.min.js', depends=[jquery])

