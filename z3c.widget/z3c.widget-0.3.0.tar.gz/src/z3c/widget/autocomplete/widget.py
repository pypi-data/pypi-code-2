from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.itemswidgets import TranslationHook
from zope.app.form.interfaces import ConversionError
from interfaces import IAutoCompleteWidget
from zope import interface

template = """%(widget_html)s
<div id="%(id)s.target" class="autoComplete"></div>
<script type="text/javascript">
new Ajax.Autocompleter('%(id)s','%(id)s.target',
'%(formUrl)s/++widget++%(id)s/suggestions'
,options={
paramName: 'value'
});
</script>
"""

class AutoCompleteWidget(SimpleInputWidget,TranslationHook):

    interface.implements(IAutoCompleteWidget)

    def __init__(self, context, request):
        super(AutoCompleteWidget, self).__init__(context, request)

    def __call__(self):
        from zc import resourcelibrary
        resourcelibrary.need('z3c.javascript.scriptaculous')
        widget_html = super(AutoCompleteWidget, self).__call__()
        
        return template % {"widget_html": widget_html,
                           "id": self.name,
                           "formUrl": self.request.getURL()
                           }

    def _toFieldValue(self, input):
        value = super(AutoCompleteWidget,self)._toFieldValue(input)
        if value == self.context.missing_value:
            return value
        for term in self.context.vocabulary:
            if self.translate(term.title) == value:
                return term.value
        raise ConversionError("Invalid value", value)
        
    def _toFormValue(self, value):
        """Converts a field value to a string used as an HTML form value.
        """
        if value == self.context.missing_value:
            return self._missing
        title = self.context.vocabulary.getTerm(value).title
        return self.translate(title)
    
    def getSuggestions(self,value):
        for term in self.context.vocabulary:
            if self.translate(term.title).lower().startswith(value.lower()):
                yield term.title

