# document schema
from yams.buildobjs import RelationDefinition

from cubicweb.schema import RQLConstraint

from cubes.vcsfile.schema import VersionedFile

class filed_under(RelationDefinition):
    subject = 'VersionedFile'
    object = 'Folder'

class root_folder(RelationDefinition):
    subject = 'Repository'
    object = 'Folder'

VersionedFile.__permissions__ = {
    'read':   ('managers', 'users'),
    'add':    ('managers', 'users',),
    'update': ('managers', 'users', 'owners'),
    'delete': ()}


# Edition conflict tool
class might_edit(RelationDefinition):
    subject = 'CWUser'
    object = 'VersionedFile',
    description = _('odt likely downloaded for edition')

# cardinalities set on relation type defined in i18ncontent

class lang(RelationDefinition):
    subject = 'VersionedFile'
    object = 'Language'

class translation_of(RelationDefinition):
    subject = 'VersionedFile'
    object = 'VersionedFile'

class pivot_lang(RelationDefinition):
    subject = 'VersionedFile'
    object = 'Boolean'
    # permissions from i18ncontent

class up_to_revision(RelationDefinition):
    """revision X of translation is up to revision Y of its master document"""
    cardinality = '?*'
    subject = ('VersionContent', 'DeletedVersionContent')
    object = ('VersionContent', 'DeletedVersionContent')
    constraints = [RQLConstraint('O content_for OVF, S content_for SVF, '
                                 'SVF translation_of OVF')]
