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
"""cubicweb-vcreview postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

pwf = add_workflow(_('patch workflow'), 'Patch')

inprogress = pwf.add_state(_('in-progress'), initial=True)
pending    = pwf.add_state(_('pending-review'))
applied    = pwf.add_state(_('applied'))
rejected   = pwf.add_state(_('rejected'))
folded     = pwf.add_state(_('folded'))
deleted    = pwf.add_state(_('deleted'))

pwf.add_transition(_('ask review'), inprogress, pending,
                   ('managers', 'users'))
pwf.add_transition(_('accept'), (inprogress, pending, deleted), applied,
                   ('managers',))
pwf.add_transition(_('reject'), (inprogress, pending, deleted), rejected,
                   ('managers',),)
pwf.add_transition(_('fold'), (inprogress, pending, deleted), folded,
                   ('managers',),)
pwf.add_transition(_('refuse'), pending, inprogress,
                   ('managers',))
# internal transition, not available through the ui
# XXX we've to put 'managers' group since transition without groups
# nor condition are fireable by anyone...
pwf.add_transition(_('file deleted'), (inprogress, pending), deleted,
                   ('managers',))
pwf.add_transition(_('reopen'), deleted, inprogress,
                   ('managers',))
