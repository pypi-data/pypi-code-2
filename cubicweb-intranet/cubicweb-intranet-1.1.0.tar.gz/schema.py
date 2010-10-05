"""schema customization for the intranet application

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from yams.buildobjs import RelationDefinition
from yams.reader import context

from cubes.card.schema import Card
from cubes.blog.schema import BlogEntry
from cubes.file.schema import File
from cubes.link.schema import Link

PERMISSIONS = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'users',),
        'delete': ('managers', 'owners',),
        'update': ('managers', 'users', 'owners',),
        }

Card.__permissions__ = PERMISSIONS
BlogEntry.__permissions__ = PERMISSIONS
File.__permissions__ = PERMISSIONS
Link.__permissions__ = PERMISSIONS

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'Event'


BASETYPES = ('Card', 'BlogEntry', 'File', 'Event', 'Link', 'Task', 'Book')
if 'VersionedFile' in context.defined:
    BASETYPES += ('VersionedFile',)
    from cubes.vcsfile.schema import VersionedFile, VersionContent
    VersionedFile.get_relation('name').fulltextindexed = True
    VersionContent.get_relation('data').fulltextindexed = True

class see_also(RelationDefinition):
    subject = BASETYPES
    object = BASETYPES

class comments(RelationDefinition):
    subject = 'Comment'
    object = BASETYPES

class tags(RelationDefinition):
    subject = 'Tag'
    object = BASETYPES
