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
"""cubicweb-trackervcs schema"""

from yams.buildobjs import RelationDefinition

from cubicweb.schema import RQLConstraint

class source_repository(RelationDefinition):
    """version controled system holding sources for this project"""
    subject = 'Project'
    object = 'Repository'
    cardinality = '??'

class introduced_by(RelationDefinition):
    subject = 'Ticket'
    object = 'Revision'
    constraints = [RQLConstraint('S concerns P, O from_repository R, P source_repository R')]


class closed_by(RelationDefinition):
    subject = 'Ticket'
    object = 'Revision'
    constraints = [RQLConstraint('S concerns P, O from_repository R, P source_repository R')]


class patch_ticket(RelationDefinition):
    subject = 'Patch'
    object = 'Ticket'
    constraints = [RQLConstraint('S patch_repository PR, R has_patch_repository PR, '
                                 'O concerns P, P source_repository R')]

