"""tracker specific entities class for imported entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

def fixed_orderby_rql(sortsdef, asc=True):
    orderby = []
    for rtype, varname in sortsdef:
        if rtype == 'priority':
            orderby.append('priority_sort_value(%s)' % varname)
        elif rtype == 'num':
            orderby.append('version_sort_value(%s)' % varname)
        else:
            orderby.append(varname)
    if asc:
        return 'ORDERBY %s' % ', '.join(orderby)
    return 'ORDERBY %s DESC' % ', '.join(orderby)


# library overrides ###########################################################

class ProjectItemMixIn(object):
    """default mixin class for commentable objects to make them implement
    the project item interface. Defined as a mixin for use by custom tracker
    templates.
    """
    @property
    def project(self):
        # XXX should we try to pick up one of the see_also projects ?
        # rset = self.req.execute('Any P WHERE P is Project, X see_also P, X eid %(x)s LIMIT 1',
        #                         {'x': self.eid})
        return None

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.project:
            return self.project.rest_path(), {}
        return 'view', {}

from cubicweb.schema import SYSTEM_RTYPES
SYSTEM_RTYPES.add('has_group_permission')
