"""entity classes for optional person entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.mixins import EmailableMixIn
from cubicweb.entities import AnyEntity, fetch_config


class Person(EmailableMixIn, AnyEntity):
    """customized class for Person entities"""
    __regid__ = 'Person'
    fetch_attrs, fetch_order = fetch_config(['surname', 'firstname'])
    rest_attr = 'surname'
    skip_copy_for = ('primary_email',)

    def dc_title(self):
        return self.name()

    def dc_long_title(self):
        return self.name(True)

    def name(self, civility=False):
        if civility and self.civility:
            return u'%s %s %s' % (self._cw._(self.civility),
                                  self.firstname or u'', self.surname or u'')
        return u'%s %s' % (self.firstname or u'', self.surname or u'')
