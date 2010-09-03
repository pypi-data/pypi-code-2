"""NDG XACML ElementTree reader module containing reader base class 

NERC DataGrid
"""
__author__ = "P J Kershaw"
__date__ = "16/03/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: reader.py 7109 2010-06-28 12:54:57Z pjkersha $"
import logging
log = logging.getLogger(__name__)

from xml.etree import ElementTree

from ndg.xacml.core import XacmlPolicyBase
from ndg.xacml.parsers import AbstractReader


class ETreeAbstractReader(AbstractReader):
    """Base class for ElementTree implementation of XACML reader
    
    @cvar TYPE: XACML type to instantiate from parsed object
    @type TYPE: NoneType"""
    TYPE = None
    
    def __init__(self):
        """Initialise ElementTree namespace map for XACML 2.0 namespaces
        
        @raise NotImplementedError: TYPE class variable must be set in a 
        derived class
        """
        if self.__class__.TYPE is None:
            raise NotImplementedError('No "TYPE" class variable set to specify '
                                      'the XACML type to instantiate')
            
        self.__namespace_map_backup = ElementTree._namespace_map.copy()
        ElementTree._namespace_map[''] = XacmlPolicyBase.XACML_2_0_POLICY_NS
        
    def __del__(self):
        """Restore original global namespace map"""
        ElementTree._namespace_map = self.__namespace_map_backup
    
    @staticmethod
    def _parse(obj):
        """Parse helper method
        @param obj: input object to parse
        @type obj: ElementTree Element, or stream object
        @return: ElementTree element
        @rtype: xml.etree.Element
        """
        if ElementTree.iselement(obj):
            elem = obj
        else:
            # Treat as stream object
            elem = ElementTree.parse(obj).getroot()
            
        return elem
         
# Set up new class as an abstract base itself             
AbstractReader.register(ETreeAbstractReader)

