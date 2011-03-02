##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Demo Itnerfaces

$Id: demo.py 105467 2009-11-03 21:56:22Z srichter $
"""
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from z3c.form import field
from z3c.formui import form
from z3c.formwidget.ckeditor import richtext, ckeditor

class IArticle(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=u'Title'
        )

    teaser = richtext.RichText(
        title=u'Teaser'
        )

    body = richtext.RichText(
        title=u'Body'
        )


class Article(object):
    zope.interface.implements(IArticle)

    title = FieldProperty(IArticle['title'])
    body = FieldProperty(IArticle['body'])


ARTICLE = Article()
ARTICLE.title = u'CKEditor Demo'
ARTICLE.body = u'This is <b>the</b> CKEditor demo.'


MinimalCKEditorWidget = ckeditor.CKEditorFieldWidgetFactory(
    {'toolbar': 'Basic', 'uiColor': '#9AB8F3'})


class DemoForm(form.EditForm):

    label = u'Edit CKEditor Article'
    fields = field.Fields(IArticle)
    fields['teaser'].widgetFactory = MinimalCKEditorWidget

    def getContent(self):
        return ARTICLE
