# -*- coding: utf-8 -*-

import grok
import zope.schema
import dolmen.content as content
import dolmen.forms.crud as crud

from html2text import html2text
from dolmen.app.layout import Index
from dolmen.app.content import IDescriptiveSchema
from dolmen.app.security import CanAddContent
from dolmen.widget.tinymce import TINYMCE_INPUT
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.index.text.interfaces import ISearchableText

_ = MessageFactory('menhir.contenttype.document')


class IDocument(IDescriptiveSchema):
    """Defines de document type.
    """
    body = zope.schema.Text(
        title=_(u"Text"),
        required=True)


class Document(content.Content):
    content.name(_("Document"))
    content.schema(IDocument)
    content.require(CanAddContent)


class SearchableTextDocument(grok.Adapter):
    grok.implements(ISearchableText)

    def getSearchableText(self):
        return (self.context.title,
                self.context.description,
                html2text(self.context.body))


class EditRichDocument(crud.FieldsCustomizer):
    grok.adapts(IDocument, Interface, Interface)

    def __call__(self, fields):
        fields['body'].mode = TINYMCE_INPUT
        return fields


class DocumentView(Index):
    grok.context(IDocument)
