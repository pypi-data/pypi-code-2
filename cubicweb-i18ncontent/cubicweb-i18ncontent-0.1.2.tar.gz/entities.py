"""entities classes for the i18ncontent component

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config


class Language(AnyEntity):
    __regid__ = 'Language'
    fetch_attrs, fetch_order = fetch_config(['code', 'name'])

    def dc_title(self):
        return '%s (%s)' % (self.code, self._cw._(self.name))
