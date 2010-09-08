from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

JqueryToolsLibrary = Library('JqueryToolsLibrary')

jquerytools = ResourceInclusion(
    JqueryToolsLibrary, 'jquery.tools.min.js', depends=[jquery])

