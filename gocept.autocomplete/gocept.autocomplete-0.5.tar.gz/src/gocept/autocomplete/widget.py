# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.autocomplete.interfaces
import string
import z3c.form.browser.text
import z3c.form.converter
import z3c.form.interfaces
import z3c.form.widget
import zc.resourcelibrary
import zope.interface
import zope.pagetemplate.interfaces
import zope.publisher.browser
import zope.security.proxy


class AutocompleteWidget(z3c.form.browser.text.TextWidget):
    zope.interface.implements(
        gocept.autocomplete.interfaces.IAutocompleteWidget)

    _javascript = """
YAHOO.namespace('gocept.autocomplete');

YAHOO.gocept.autocomplete.init_${id_} = new function() {
    this.datasource = new YAHOO.widget.DS_XHR("${url}", ["\\n"]);
    this.datasource.responseType = YAHOO.widget.DS_XHR.TYPE_FLAT;
    this.datasource.scriptQueryParam = "q";
    this.autocomp = new YAHOO.widget.AutoComplete(
        "${id}", "${id}-container", this.datasource);
    this.autocomp.prehighlightClassName = "yui-ac-prehighlight";
    this.autocomp.typeAhead = ${typeAhead};
    this.autocomp.minQueryLength = ${minQueryLength};
    this.autocomp.useShadow = true;
    this.autocomp.delimChar = "${delimchar}";
    this.autocomp.doBeforeExpandContainer = function(textbox, container, query, results) {
        var pos = YAHOO.util.Dom.getXY(textbox);
        pos[1] += YAHOO.util.Dom.get(textbox).offsetHeight + 2;
        YAHOO.util.Dom.setXY(container, pos);
        return true;
    };
}

YAHOO.util.Event.onDOMReady(YAHOO.gocept.autocomplete.init_${id_});
"""

    def __init__(self, *args, **kw):
        super(AutocompleteWidget, self).__init__(*args, **kw)
        self.delimchar = ''
        self.typeAhead = 'true'
        self.minQueryLength = 1
        self.addClass(u'autocomplete')

    def render(self):
        zc.resourcelibrary.need("yui-autocomplete")
        return super(AutocompleteWidget, self).render()

    def input_field(self):
        class Dummy(object):
            pass
        parent = Dummy()
        zope.interface.alsoProvides(parent, z3c.form.interfaces.ITextWidget)
        super_template = zope.component.getMultiAdapter(
            (self.context, self.request, self.form, self.field,
             parent),
            zope.pagetemplate.interfaces.IPageTemplate, name=self.mode)
        return super_template(self)

    def javascript(self):
        context_url = str(zope.component.getMultiAdapter(
            (self.form.context, self.request), name='absolute_url'))

        search_url = "%s/@@%s/++widget++%s/@@autocomplete-search" % (
            context_url, self.form.__name__, self.name.split('.')[-1])

        return string.Template(self._javascript).substitute(dict(
            id=self.id, id_=self.id.replace('-', '_'),
            delimchar=self.delimchar, typeAhead=self.typeAhead,
            minQueryLength=self.minQueryLength, url=search_url))


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        gocept.autocomplete.interfaces.ISearchableSource,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def AutocompleteFieldWidget(field, source, request):
    return z3c.form.widget.FieldWidget(field, AutocompleteWidget(request))


class SearchView(zope.publisher.browser.BrowserView):
    def __call__(self):
        # XXX security!!
        context = zope.security.proxy.removeSecurityProxy(self.context)
        query = self.request.get("q")
        if query:
            return u"\n".join(context.field.source.search(query))
        else:
            return u""
