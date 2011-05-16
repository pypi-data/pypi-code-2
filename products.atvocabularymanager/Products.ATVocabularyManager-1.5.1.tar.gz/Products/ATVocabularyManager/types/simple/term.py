# File: SimpleVocabularyTerm.py
"""\
A simple Key-Value term, where Value may be i18nized using LinguaPlone.

RCS-ID $Id: SimpleVocabularyTerm.py 3172 2004-10-13 21:18:00Z yenzenz $
"""
# Copyright (c) 2004-2006 by BlueDynamics Alliance - Klein & Partner KEG, Austria
#
# BSD-like licence, see LICENCE.txt
#
__author__  = 'Jens Klein <jens@bluedynamics.com>'
__docformat__ = 'plaintext'

from zope import event

from Products.ATVocabularyManager.config import *
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import *
else:
    from Products.Archetypes.atapi import *

from AccessControl import ClassSecurityInfo
try:
    from Products.Archetypes.interfaces.vocabulary import IVocabularyTerm
except ImportError:
    from Products.ATVocabularyManager.backports import IVocabularyTerm

from Products.Archetypes.debug import deprecated
from Products.ATVocabularyManager.tools import registerVocabularyTerm
from Products.ATVocabularyManager.event import find_toplevel_vocab, TermRenamedEvent
from Products.ATVocabularyManager.config import PROJECTNAME

term_schema = BaseContent.schema + Schema()

term_schema['id'] = BaseContent.schema['id'].copy()
term_schema['id'].widget.label = "Key"
term_schema['id'].widget.label_msgid = "label_key"
term_schema['id'].widget.description = "Should not contain spaces, underscores or mixed case."
term_schema['id'].widget.description_msgid = "help_key"
term_schema['id'].widget.i18n_domain = "atvocabularymanager"

term_schema['title'] = BaseContent.schema['title'].copy()
term_schema['title'].widget.label = "Value"
term_schema['title'].widget.label_msgid = "label_value"
term_schema['title'].widget.i18n_domain = "atvocabularymanager"



class SimpleVocabularyTerm(BaseContent):
    security = ClassSecurityInfo()
    portal_type = meta_type = 'SimpleVocabularyTerm'
    archetype_name = 'Simple Vocabulary Term'
    _at_rename_after_creation = True

    __implements__ = getattr(BaseContent,'__implements__',()) + (IVocabularyTerm,)

    schema = term_schema

    aliases = {
        '(Default)' : 'base_view',
        'view' : 'base_view',
        'edit' : 'base_edit',
    }

    # Methods
    # methods from Interface IVocabularTerm


    def getTermKey(self):
        """
        """
        if not HAS_LINGUA_PLONE or self.isCanonical():
            return self.getId()
        else:
            return self.getCanonical().getId()

    def getTermValue(self, lang=None):
        """
        """
        if not lang is None:
            # if we ask for a specific language, we try to
            # provide it
            obj = self.getTranslation(lang) or self
            # if not found, we return the title of the current term
        else:
            obj = self
        return obj.Title().decode('utf8')

    def getTermKeyPath(self):
        # terms of flat vocabularies can savely return their key
        return [self.getTermKey(),]


    def getVocabularyKey(self):
        ''' returns the key of the field '''
        deprecated("please use the IVocabularyTerm compatible method 'getTermKey'")
        return self.getTermKey()

    def getVocabularyValue(self, **kwargs):
        ''' returns the value of the field. The value is a processed value '''
        deprecated("please use the IVocabularyTerm compatible method 'getTermValue'")
        return self.getTermValue()

    def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
        request = REQUEST or self.REQUEST
        values = request.form

        if values.has_key('title'):
            orig_title = self.Title()

        BaseContent.processForm(self, data, metadata, REQUEST, values)

        if values.has_key('title'):
            new_title = values['title']
            vocab = find_toplevel_vocab(self)
            event.notify(TermRenamedEvent(orig_title, new_title, self, vocab))

    def update(self, *args, **kwargs):
        if kwargs.has_key('title'):
            orig_title = self.Title()

        BaseContent.update(self, *args, **kwargs)

        if kwargs.has_key('title'):
            new_title = kwargs['title']
            vocab = find_toplevel_vocab(self)
            event.notify(TermRenamedEvent(orig_title, new_title, self, vocab))

    edit = update

    # uncomment lines below when you need
    factory_type_information={
        'allowed_content_types':() ,
        'allow_discussion': 0,
        'immediate_view':'simplevocabulary_view',
        'global_allow':0,
        'filter_content_types':1,
        }


    actions=  (


          )


registerType(SimpleVocabularyTerm, PROJECTNAME)
registerVocabularyTerm(SimpleVocabularyTerm,'SimpleVocabulary')
registerVocabularyTerm(SimpleVocabularyTerm, 'SortedSimpleVocabulary')
