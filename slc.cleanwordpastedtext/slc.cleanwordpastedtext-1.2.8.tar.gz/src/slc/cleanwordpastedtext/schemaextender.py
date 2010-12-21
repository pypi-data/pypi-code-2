import logging

from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

try:
    from Products.LinguaPlone.utils import generateMethods
    generateMethods = generateMethods # PyFlakes
except ImportError:
    generateMethods = None 

from Products.Archetypes import atapi
from Products.CMFPlone import PloneMessageFactory as _

log = logging.getLogger('slc.cleanwordpastedtext.schemaextender.py')

LANGUAGE_INDEPENDENT_INITIALIZED = '_languageIndependent_initialized_slc_cleanwordpastedtext'

class ExtensionFieldMixin:
    """
        archetypes.schemaextender.field.ExtensionField's getMutator needs to be
        overwritten, to play nicely with the named mutators we get from Lingua-
        Plone's generateMethods magic.
        Otherwise languageIndependent field values would not get propagated to the
        translations when the canonical is edited.
        NB: Only tested with LinguaPlone 2.2 - For later versions, it might not be
        necessary any more! Please check if you use a later LP version...
    """
    def getMutator(self, instance):
        def mutator(value, **kw):
            self.set(instance, value, **kw)
        methodName = getattr(self, 'mutator', None)
        if methodName is None:  # Use default setter
            return mutator
        
        method = getattr(instance, methodName, None)
        if method is None:   # Use default setter
            return mutator
        return method
        

class ExtendedBooleanField(ExtensionFieldMixin, ExtensionField, atapi.BooleanField):
    """ """

class SchemaExtender(object):
    """ Extend a file to add the 'Auto-translate checkbox' """
    implements(ISchemaExtender)

    _fields = [
            ExtendedBooleanField('cleanWordPastedText',
                schemata='settings',
                languageIndependent=True,
                default=True,
                accessor='getCleanWordPastedText',
                widget=atapi.BooleanWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    label = _(
                        u'label_clean_word_pasted_text', 
                        default=u'Automatically clean MSWord pasted text?',
                    ),
                    description=_(
                        u'description_clean_word_pasted_text', 
                        default=u"Choose this option if you want the "
                        "HTML of this object's Rich-Text fields to be "
                        "cleaned up. <br/> WARNING: This may result in loss "
                        "of text formatting."
                    ),
                ),
            ),
            ]

    def getFields(self):
        """ get fields """
        return self._fields

    def __init__(self, context):
        self.context = context
        
        if generateMethods is not None:
            klass = context.__class__
            if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
                fields = [field for field in self._fields if field.languageIndependent]
                generateMethods(klass, fields)
                log.info("called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
                setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

