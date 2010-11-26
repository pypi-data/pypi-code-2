from Acquisition import aq_inner
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.interfaces import (
    ILangCharset,
)

class LangCharset(object):
    implements(ILangCharset)
    def __init__(self, context):
        self.context = context

    def lang_charset(self):
        context = aq_inner(self.context)
        properties = getToolByName(context, 'portal_properties')
        if len(properties.mailhost_properties.getProperty('lang_charset')) != 0:
            lang_charset_tuples = [
                lc.split('|') for lc in properties.mailhost_properties.getProperty('lang_charset')
            ]
            lang_charset = dict(lang_charset_tuples)
            return lang_charset

    def effective_lang(self):
        context = aq_inner(self.context)
        membership = getToolByName(context, 'portal_membership')
        properties = getToolByName(context, 'portal_properties')
        is_member_lang = properties.mailhost_properties.getProperty('is_member_lang_effective')
        member_lang = membership.getAuthenticatedMember().getProperty('language')
        if is_member_lang and member_lang != '' and member_lang is not None:
            return member_lang
        else:
            language_tool = getToolByName(context, 'portal_languages')
            return language_tool.getPreferredLanguage()

    def effective_charset(self):
        lang = self.effective_lang()
        if lang:
            return self.lang_charset().get(lang)
