from tw import framework
from tw.api import Link, CSSLink, JSLink
from rum import app
from tw.dojo.dojo import DojoFilteringSelect, DojoBase, DojoLink, dojo_js, tundra_css, dojo_css
from tw.forms import FormField

modname = "tw.rum"
autocompletion_store_js=JSLink(modname=modname,filename="static/autocompletion.js", javascript=[dojo_js])

class AutoCompletion(FormField, DojoBase):
    dojoType = 'dijit.form.FilteringSelect'
    require=['dijit.form.FilteringSelect','dojox.data.dom']
    javascript=[autocompletion_store_js]
    css=[tundra_css]
    template = "genshi:tw.rum.templates.autocompletion"
    params=['completion_url', 'search_delay']
    isDebug=True
    search_delay=500
