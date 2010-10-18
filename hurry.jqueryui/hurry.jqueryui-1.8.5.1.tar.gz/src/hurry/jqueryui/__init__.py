from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery
try:
    from hurry.jqueryui._themes import *
except ImportError:
    pass

jqueryui_lib = Library('jqueryui', 'jqueryui-build')

jqueryui = ResourceInclusion(jqueryui_lib, 'jquery-ui.js', depends=[jquery],
                             minified='jquery-ui.min.js')

