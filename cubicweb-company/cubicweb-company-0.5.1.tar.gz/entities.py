"""this contains the template-specific entities' classes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter
from cubicweb.selectors import is_instance

class Division(AnyEntity):
    """customized class for Division entities"""
    __regid__ = 'Division'
    fetch_attrs, fetch_order = fetch_config(['name'])

class Company(Division):
    """customized class for Company entities"""
    __regid__ = 'Company'

class CompanyITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Company')
    tree_relation = 'subsidiary_of'
