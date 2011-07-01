from zope.app.form.browser.textwidgets import TextWidget
from zope.schema.interfaces import IFromUnicode

from field import Link

class LinkWidget(TextWidget):
    type = 'Link'
    size = '60'
    
    def _toFieldValue(self, input):
        if self.convert_missing_value and input == self._missing:
            value = self.context.missing_value
        else:
            assert IFromUnicode.providedBy(self.context)

            try:
                value = self.context.fromUnicode(input)
            except ValueError, v:
                raise ConversionError(_("Invalid link"), v)
        return value
