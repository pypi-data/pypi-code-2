"""entity classes for task entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config, adapters
from cubicweb.selectors import is_instance

class Task(AnyEntity):
    """customized class for Task entities"""
    __regid__ = 'Task'
    fetch_attrs, fetch_order = fetch_config(['title'])

    def dc_title(self):
        return self.title


class TaskITreeAdapter(adapters.ITreeAdapter):
    # XXX graph structure, not tree structure
    __select__ = is_instance('ITree')
    tree_relation = 'depends_on'
    child_role = 'subject'
    parent_role = 'object'
