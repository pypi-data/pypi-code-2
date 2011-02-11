# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-vcreview schema"""

from yams.buildobjs import EntityType, RelationDefinition, String

from cubicweb.schema import WorkflowableEntityType, RQLConstraint

# XXX nosylist. notifications: send all review (eg task + commment) at wf transition time


class has_patch_repository(RelationDefinition):
    """the patch repository will have patch entities generated for file stored
    in it.
    """
    subject = 'Repository'
    object = 'Repository'
    cardinality = '*?'


# the patch entity #############################################################

class Patch(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users'),
        'add': (), # created by an internal session in a looping task
        'update': ('managers', 'users'),
        'delete': ('managers',),
        }

class patch_repository(RelationDefinition):
    # shortcut for P patch_revision VC, VC revision REV, REV from_repository R
    __permissions__ = {
        'read': ('managers', 'users'),
        'add': (), # created by an internal session in a looping task
        'delete': (),
        }
    subject = 'Patch'
    object = 'Repository'
    cardinality = '1*'
    composite = 'subject'
    inlined = True

class patch_revision(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users'),
        'add': (), # created by an internal session in a looping task
        'delete': (),
        }
    subject = 'Patch'
    object = ('VersionContent', 'DeletedVersionContent')
    cardinality = '+*'

class applied_at(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users'),
        'add': ('managers',),
        'delete': ('managers',),
        }
    subject = 'Patch'
    object = 'Revision'
    cardinality = '??'
    constraints = [RQLConstraint('S patch_repository PR, O from_repository R, '
                                 'R has_patch_repository PR')]


# ability to reference diff chunks #############################################

class InsertionPoint(EntityType):
    __unique_together__ = [('id', 'point_of')]
    id = String(maxsize=100, indexed=True)

class point_of(RelationDefinition):
    subject = 'InsertionPoint'
    object = 'VersionContent'
    cardinality = '1*'
    composite = 'object'
    inlined = True


# activities ###################################################################

class has_activity(RelationDefinition):
    subject = ('Patch', 'InsertionPoint')
    object = 'Task'
    cardinality = '*?'
    composite = 'subject'


# comments #####################################################################

class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Patch', 'InsertionPoint')


# notification #################################################################

class nosy_list(RelationDefinition):
    subject = ('Repository', 'Patch', 'Task')
    object = 'CWUser'

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'Repository'
