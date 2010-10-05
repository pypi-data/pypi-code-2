"""specific view classes for intranet

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import is_instance

from cubes.tag.views import TagsCloudBox

TagsCloudBox.visible = True
TagsCloudBox.__select__ = TagsCloudBox.__select__ & is_instance('BlogEntry', 'Link', 'Card', 'File')
