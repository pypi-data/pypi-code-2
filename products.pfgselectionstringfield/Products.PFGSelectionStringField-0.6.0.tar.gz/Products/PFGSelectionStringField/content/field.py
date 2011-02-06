import cgi
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes.public import (
    DisplayList,
    Schema,
    LinesField,
    StringField,
    LinesWidget,
    SelectionWidget,
)
from Products.PloneFormGen.content.fields import FGSelectionField
from Products.PloneFormGen.content.fieldsBase import (
    BaseFieldSchemaStringDefault,
    finalizeFieldSchema,
    vocabularyOverrideField
)
from Products.PFGSelectionStringField.config import PROJECTNAME

vocabularyField = \
    LinesField('fgVocabulary',
        searchable=0,
        required=0,
        widget=LinesWidget(label='Options',
            description="""
                Use one line per option.
                Note that this may be overridden dynamically.
                [Note, you may optionally use a "value|label|description" format.]
                """,
            i18n_domain = "ploneformgen",
            label_msgid = "label_fgvocabulary_text",
            description_msgid = "help_fgvocabulary_text",
            ),
        )

class StringVocabularyField(StringField):
    """
    Parent for fields that have vocabularies.
    Overrides Vocabulary so that we can get the value from the instance
    """

    security  = ClassSecurityInfo()

    security.declarePublic('Vocabulary')
    def Vocabulary(self, content_instance=None):
        """
        Returns a DisplayList.
        """
        # if there's a TALES override, return it as a DisplayList,
        # otherwise, build the DisplayList from fgVocabulary

        fieldContainer = content_instance.findFieldObjectByName(self.__name__)

        vl = fieldContainer.getFgTVocabulary()
        if vl is not None:
            return DisplayList( data=vl )

        res = []
        for line in fieldContainer.fgVocabulary:
            lsplit = line.split('|')
            if len(lsplit) == 3:
                item = (lsplit[0],(lsplit[1], lsplit[2]))
            elif len(lsplit) == 2:
                item = (lsplit[0],(lsplit[1], None))
            else:
                item = (lsplit[0],(lsplit[0], None))
            res.append(item)
        return res

class SelectionStringWidget(SelectionWidget):
    _properties = SelectionWidget._properties.copy()
    _properties.update({
        'macro' : "selection_string",
        })

    security = ClassSecurityInfo()

class PFGSelectionStringField(FGSelectionField):
    """Selection String Field"""

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        vocabularyField,
        vocabularyOverrideField,
        StringField('fgFormat',
            searchable=0,
            required=0,
            default='flex',
            enforceVocabulary=1,
            vocabulary='formatVocabDL',
            widget=SelectionWidget(
                label='Presentation Widget',
                i18n_domain = "ploneformgen",
                label_msgid = "label_fgformat_text",
                description_msgid = "help_fgformat_text",
                ),
        ),
    ))

    del schema['hidden']

    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    portal_type = meta_type = 'PFGSelectionStringField'
    archetype_name = 'Selection String Field'
    content_icon = 'ListField.gif'
    typeDescription= 'A selection field with string field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        FGSelectionField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringVocabularyField('fg_selection_field',
            searchable=0,
            required=0,
            widget=SelectionStringWidget(),
            vocabulary = '_get_selection_vocab',
            enforceVocabulary=1,
            write_permission = View,
            )

    def htmlValue(self, REQUEST):
        """ Return value instead of key """

        utils = getToolByName(self, 'plone_utils')
        charset = utils.getSiteEncoding()

        value = REQUEST.form.get(self.__name__, '')

        # note that vocabulary items are in unicode;
        # so, we must decode before lookup
        vu = value.decode(charset)

        vocabulary = self.fgField.Vocabulary(self)
#        v = vocabulary.getValue(vu) or vu
#        v = vu
        item = dict(vocabulary).get(vu)
        name = '%s_%s' %(self.__name__, vu)
        desc = REQUEST.form.get(name, None)
        if item is None:
            return vu
        elif desc is None:
            return cgi.escape(item[0].encode(charset))
        else:
            return '%s<br />%s' %(cgi.escape(item[0].encode(charset)), cgi.escape(desc.encode(charset)))



registerATCT(PFGSelectionStringField, PROJECTNAME)
