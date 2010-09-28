# pylint:  disable-msg=E0611,F0401
"""tracker application'schema

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.constraints import SizeConstraint
from yams.buildobjs import (
    EntityType, RelationType, RelationDefinition,
    SubjectRelation, ObjectRelation, RichString, String, Date)

from cubicweb.schema import (
    RQLConstraint, RQLVocabularyConstraint,
    ERQLExpression, RRQLExpression, WorkflowableEntityType)

from cubes.tracker.schemaperms import (
    sexpr, oexpr, xexpr, restricted_oexpr, xperm)


class Project(EntityType):
    """a project is a logical group of tasks/information which produce a final value. That
    may be a software or documentation project, a web site or whatever.
    """
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff',),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', 'owners'),
        }
    ## attributes
    name      = String(required=True, fulltextindexed=True, unique=True, maxsize=64)
    summary   = String(fulltextindexed=True, maxsize=128,
                       description=_('one line description of the project'))

    description = RichString(fulltextindexed=True, default_format='text/rest',
                             description=_('more detailed description'))

    ## relations
    uses = SubjectRelation('Project', description=_('project\'s dependencies'))
    subproject_of = SubjectRelation('Project', composite='object', cardinality='?*')


class uses(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }


class Version(WorkflowableEntityType):
    """a version is defining the content of a particular project's release"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        # right to add Version is actually granted on the version_of relation
        'add':    ('managers', 'users'),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', ),
        }

    ## attributes
    num              = String(required=True, fulltextindexed=True, indexed=True,
                              constraints=[SizeConstraint(16)],
                              description=_('release number'))
    description      = RichString(fulltextindexed=True, default_format='text/rest',
                                  description=_('targets for this version'))
    starting_date   = Date(description=_('estimated starting date'))
    prevision_date   = Date(description=_('estimated publication date'))
    publication_date = Date(description=_('actual publication date'))

    ## relations
    version_of = SubjectRelation('Project', cardinality='1*', composite='object')
    todo_by = SubjectRelation('CWUser',
                              constraints=[RQLConstraint('O in_state ST, ST name "activated"'),
                                           RQLVocabularyConstraint('O in_group G, G name "staff"')],
                              description=_('users responsible for this version'))
    conflicts = SubjectRelation('Version',
                                constraints=[RQLVocabularyConstraint('S version_of PS, O version_of PO, EXISTS(PS uses PO) OR EXISTS(PO subproject_of PS)')],
                                description=_('client project\'s version conflicting with this version'))
    depends_on = SubjectRelation('Version',
                                 constraints=[RQLVocabularyConstraint('S version_of PS, O version_of PO, EXISTS(PS uses PO) OR EXISTS(PO subproject_of PS)')],
                                 description=_('client project\'s version dependency for this version'))


class Ticket(WorkflowableEntityType):
    """a ticket is representing some kind of work to do (or done) on a project
    (bug fix, feature request...)
    """
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        # right to add Ticket is actually granted on the concerns relation
        'add':    ('managers', 'users',),
        # client can only modify tickets when they are in the "open" state
        'update': ('managers', 'staff', xexpr('developer'),
                   ERQLExpression(xperm('client')+', X in_state S, S name "created"'),),
        'delete': ('managers', ),
        }

    ## attributes
    title = String(required=True, fulltextindexed=True,
                   constraints=[SizeConstraint(128)])

    description = RichString(fulltextindexed=True, default_format='text/rest',
                             description=_("give any useful information (to "
                                           "describe a bug think to give your "
                                           "configuration and some way to reproduce"
                                           " it whenever possible)"))
    priority = String(required=True, internationalizable=True,
                      vocabulary=[_('important'), _('normal'), _('minor')],
                      description=_("importance"), default='normal')
    type = String(required=True, internationalizable=True,
                  vocabulary=[_('bug'), _('enhancement'), _('task')],
                  description=_("type"), default='bug')

    ## relations
    concerns = SubjectRelation('Project', cardinality='1*', composite='object')
    appeared_in = SubjectRelation(('Version'), cardinality='?*',
                                   constraints=[RQLConstraint('S concerns P, O version_of P'),
                                                RQLVocabularyConstraint('O in_state ST, ST name "published"')],
                                   description=_("version in which a bug has been encountered"))
    done_in = SubjectRelation(('Version'), cardinality='?*',
                              constraints=[RQLConstraint('S concerns P, O version_of P'),
                                           RQLVocabularyConstraint('O in_state ST, NOT ST name "published"')],
                              description=_("version in which this ticket will be / has been  done"))

    identical_to = SubjectRelation('Ticket',
                                   constraints=[RQLConstraint('S concerns P, O concerns P')])
    depends_on = SubjectRelation('Ticket',
                                 description=_("ticket which has to be done to complete this one"),
                                 constraints=[RQLVocabularyConstraint(
                                     'S concerns P, EXISTS(O concerns P) '
                                     'OR EXISTS(O concerns PS, '
                                     'EXISTS(P uses P2) OR '
                                     'EXISTS(P2 subproject_of P))')])





# extra relation definitions ##################################################

class see_also(RelationDefinition):
    symmetric = True
    subject = ('Project', 'Ticket')
    object = ('Project', 'Ticket')


class require_permission(RelationDefinition):
    subject = ('Project', 'Version', 'Ticket')
    object = 'CWPermission'

class has_group_permission(RelationDefinition):
    """short cut relation for 'U in_group G, P require_group G' for efficiency
    reason. This relation is set automatically, you should not set this.
    """
    subject = 'CWUser'
    object = 'CWPermission'
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'delete': ('managers',),
        }

# relation types permissions ##################################################

class subproject_of(RelationType):
    """link a ticket to the version in which it has been done"""
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', RRQLExpression('U has_update_permission O', 'O')),
        'delete': ('managers', 'staff', RRQLExpression('U has_update_permission O', 'O')),
    }

class version_of(RelationType):
    """link a version to its project. A version is necessarily linked to one and
    only one project.
    """
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff', oexpr('client'),),
        'delete': ('managers', ),
        }

class todo_by(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'delete': ('managers',),
        }

class conflicts(RelationType):
    symmetric = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer'),),
        'delete': ('managers', 'staff', sexpr('developer'),),
        }

class concerns(RelationType):
    """link a ticket to its project. A ticket is necessarily linked to one and
    only one project.
    """
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff',),
    }

class done_in(RelationType):
    """link a ticket to the version in which it has been done"""
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        # XXX should require permission on the ticket or on the version, or both?
        # XXX should check the state of a ticket
        'add':    ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "planned"', 'client'),),
        'delete': ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "planned"', 'client'),),
    }

class appeared_in(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        # XXX should require permission on the ticket or on the version, or both?
        'add':    ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "published"', 'developer', 'client'),),
        'delete': ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "published"', 'developer', 'client'),),
    }

class depends_on(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

