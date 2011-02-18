"""
abl.jquery.plugin.form resources

"""

from tw.api import JSLink, CSSLink
from abl.jquery.core import jquery_js
from abl.jquery.plugins.blockUI import jquery_blockUI_js

modname = __name__

# declare here resources for your jQuery-plugin. The most probably look like this:

form_js = JSLink(filename="static/javascript/jquery.form.js",
                 javascript=[jquery_js],
                 modname=modname)

form_widget_css = CSSLink(filename="static/css/form_widget.css",
                          modname=modname)

form_widget_js = JSLink(filename="static/javascript/jquery.form.widget.js",
                        javascript=[form_js, jquery_blockUI_js],
                        css=[form_widget_css],
                        modname=modname)

# Local Variables:
# mode:python
# End:
