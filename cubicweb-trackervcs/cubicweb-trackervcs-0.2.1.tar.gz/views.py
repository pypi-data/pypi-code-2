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
"""cubicweb-trackervcs views"""

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance, score_entity
from cubicweb.web import uicfg, formwidgets as wdg
from cubicweb.web.views import primary

_pvs = uicfg.primaryview_section
# _abaa = uicfg.actionbox_appearsin_addmenu
# _afs = uicfg.autoform_section
# _affk = uicfg.autoform_field_kwargs

_pvs.tag_subject_of(('Project', 'source_repository', '*'), 'attributes')

