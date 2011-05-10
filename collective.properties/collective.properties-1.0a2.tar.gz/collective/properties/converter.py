from zope.component import adapts
from zope.schema.interfaces import IBytesLine, IBytes, IChoice

from Products.CMFPlone.utils import safe_unicode, normalizeString

from z3c.form.interfaces import ITextAreaWidget, ITextWidget
from z3c.form.converter import BaseDataConverter, SequenceDataConverter

from collective.properties.interfaces import IBytesLineTuple, \
    ISpecialSelectWidget, ISpecialOrderedSelectWidget


class BytesLineTupleTextAreaDataConverter(BaseDataConverter):
    """A special converter between BytesLineTuple field and text area widget.
    
    Field is a tuple of utf-8 encoded strings while widget needs one utf-8
    encodded string containing above mentioned strings joined by line break.
    """

    adapts(IBytesLineTuple, ITextAreaWidget)

    def toWidgetValue(self, value):
        """Convert from Python sequence (tuple or list) to HTML representation:
        unicode string with line breaks between each sequence item.
        """
        if value is self.field.missing_value:
            return u''

        # we keep value in bytes field to be compliant with OFS.PropertyManager
        return u'\r\n'.join([safe_unicode(v) for v in value])

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        
        return collectionType([v.encode('utf-8') for v in value.split(u'\r\n')])

class BytesLineTextDataConverter(BaseDataConverter):
    """A special converter between bytes line field and text widget."""

    adapts(IBytesLine, ITextWidget)

    def toWidgetValue(self, value):
        """Converts string to unicode"""
        if value is self.field.missing_value:
            return u''

        return safe_unicode(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        
        return value.encode('utf-8')

class BytesTextAreaDataConverter(BytesLineTextDataConverter):
    """A special converter between bytes field and text area widget."""

    adapts(IBytes, ITextAreaWidget)

class ChoiceSpecialSelectDataConverter(SequenceDataConverter):
    """A special converter between choice field and special select widget.
    It won't break if current field values is not present inside widget terms.
    
    Here we also are not using term token, but only value. This widget we adapt
    here works only with term value and title. Token is not used as
    it won't work for terms containing non-ascii characters in it's value and at
    the same time to stay compliant with IPropertyManager form.
    """
    adapts(IChoice, ISpecialSelectWidget)

    def toWidgetValue(self, value):
        widget = self.widget
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return []
        
        # Look up the term in the terms
        terms = widget.updateTerms()
        if value not in terms:
            return []
        
        # ensure we get unicode for select widget, otherwise it breaks
        return [value]

    def toFieldValue(self, value):
        widget = self.widget
        if not len(value) or value[0] == widget.noValueToken:
            return self.field.missing_value
        
        # as we use widget that only uses term values this means
        # we got ready to use value and ensure we value is within
        # vocabulary terms
        terms = widget.updateTerms()
        if value[0] not in terms:
            return self.field.missing_value
        
        return value[0]

class BytesLineTupleSpecialOrderedSelectDataConverter(BaseDataConverter):
    """A special converter between bytesline tuple field and special ordered
    select widget.
    We use it for the same purposes as above defined converter for choice field.
    """

    adapts(IBytesLineTuple, ISpecialOrderedSelectWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        terms = widget.terms
        return [entry for entry in value if entry in terms]

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if widget.terms is None:
            widget.updateTerms()
        
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        
        terms = widget.terms
        return collectionType([entry for entry in value if entry in terms])
