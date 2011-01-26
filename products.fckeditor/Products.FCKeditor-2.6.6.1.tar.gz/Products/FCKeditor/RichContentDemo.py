#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""

"""
__author__  = 'Jean-mat <jean-mat@ingeniweb.com>'
__docformat__ = 'restructuredtext'
  
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.atapi import AnnotationStorage

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.document import ATDocument, ATDocumentSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.interfaces import IATDocument

from Products.FCKeditor.config import PROJECTNAME
from Products.FCKeditor.FckWidget import FckWidget

from Products.CMFPlone import PloneMessageFactory as _


_sampleToolBar  = """[
['Source','Preview','-','Templates'],
['Cut','Copy','Paste','PasteText','PasteWord','-','Print','rtSpellCheck'],
['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
['OrderedList','UnorderedList','-','Outdent','Indent'],
['Link','Unlink','Anchor','Image'],
['Style','FontFormat'],
['FitWindow']
]"""
      

FCKDocumentSchema = ATDocumentSchema.copy() + Schema((
    TextField('smalltext',
              required=False,
              searchable=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/html',),
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              widget = FckWidget(
                        description = '',
                        label = _(u'label_small_text', default=u'Small Text'),
                        rows=10,
                        width = '80%',
                        height ='200px',
                        fck_toolbar = 'Basic',
                        allow_server_browsing = 0,
                        allow_content_upload = zconf.ATDocument.allow_document_upload),
    ),
    TextField('text2',
              required=False,
              searchable=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/html',), 
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              widget = FckWidget(
                        description = '',
                        label = _(u'label_text2', default=u'Text 2'),
                        rows=10,
                        width = '80%',
                        height ='200px',
                        start_expanded = False, 
                        linkbyuid = 0,
                        # folder attachments must exist in this case
                        fck_force_other_path = '/attachments',
                        fck_force_other_root = '/attachments',
                        fck_toolbar = 'Custom',
                        fck_custom_toolbar = _sampleToolBar,
                        allow_content_upload = zconf.ATDocument.allow_document_upload),
    ),    
    ),
    marshall=RFC822Marshaller()
    )

finalizeATCTSchema(FCKDocumentSchema)
FCKDocumentSchema.moveField('smalltext', before='text')
FCKDocumentSchema.moveField('text2', before='text')



class FCKDocument(ATDocument):
    """A page in the site. Can contain rich text."""

    schema = FCKDocumentSchema

    portal_type = meta_type = 'FCKDemoDocument'
    archetype_name = 'FCK Page Demo'
    _atct_newTypeFor = {}
    content_icon = "document_icon.gif"
    immediate_view = 'base_view'
    default_view = 'base_view'
    filter_content_types = True    
    global_allow = True

    __implements__ = ATDocument.__implements__
    
  
    

registerATCT(FCKDocument, PROJECTNAME)
