from OFS.Image import File
from StreamingFile import StreamingFile
from Products.CMFCore.permissions import View

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField, FileField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget, FileWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.public import PrimaryFieldMarshaller

from Products.ExternalStorage.ExternalStorage import ExternalStorage

from Products.ExternalExample.config import ARTICLE_GROUPS, PROJECTNAME

schema = BaseSchema + Schema((

    StringField('group',
        vocabulary = ARTICLE_GROUPS,
        widget = SelectionWidget(),
    ),

    StringField('blurb',
        searchable = 1,
        widget = TextAreaWidget(),
    ),

    FileField('file_normal',
        widget = FileWidget(),
    ),

    FileField('file',
        required = 1,
        primary = 1,
        storage = ExternalStorage(
            prefix = 'files',
            rename = True,
        ),
        widget = FileWidget(
            label = 'File',
        ),
    ),

    TextField('body',
        searchable = 1,
        default_output_type = 'text/html',
        allowable_content_types = (
            'text/plain',
            'text/structured',
            'text/restructured',
            'text/html',
            'application/msword',
        ),
        widget = RichWidget(
            label='Body',
        ),
    ),

    ), marshall=PrimaryFieldMarshaller(),

)


class ExternalArticle(BaseContent):
    """This is a sample article, it has an overridden view for show,
    but this is purely optional
    """

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/article_view',
        'permissions': (View,)
        },)

    def stream(self, **kwargs):
        """return the file with proper content type"""
        REQUEST=kwargs.get('REQUEST',self.REQUEST)
        RESPONSE=kwargs.get('RESPONSE',REQUEST.RESPONSE)
        file = self.getFile(useIterator=1)
        # retrieve the content type this way
        ct = self.getContentType(self, 'field')
        path = self.getFilepath(self, 'field')
        # what about size?!?
        return StreamingFile(self.getId(),self.Title(),file,ct).__of__(self.aq_parent).index_html(REQUEST,RESPONSE,path)

    # make it directly streamable when entering the object URL
    index_html = stream

registerType(ExternalArticle, PROJECTNAME)
