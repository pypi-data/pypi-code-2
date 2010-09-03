"""NDG XACML Context Resource type

NERC DataGrid
"""
__author__ = "P J Kershaw"
__date__ = "24/03/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: resource.py 7098 2010-06-25 13:51:24Z pjkersha $"
from ndg.xacml.core.context import RequestChildBase


class Resource(RequestChildBase):
    """XACML Context Resource type
    
    @cvar ELEMENT_LOCAL_NAME: XML local element name for the resource
    @type ELEMENT_LOCAL_NAME: string
    @cvar RESOURCE_CONTENT_ELEMENT_LOCAL_NAME: XML local element name for the
    resource content
    @type RESOURCE_CONTENT_ELEMENT_LOCAL_NAME: string
    
    @ivar __resourceContent: resource content
    @type __resourceContent: any
    """
    ELEMENT_LOCAL_NAME = 'Resource'
    RESOURCE_CONTENT_ELEMENT_LOCAL_NAME = 'ResourceContent'
    
    __slots__ = ('__resourceContent',)
    
    def __init__(self):
        """Initial resource content instance variable"""
        super(Resource, self).__init__()
        self.__resourceContent = None

    def _get_resourceContent(self):
        """Get resource content
        @return: content
        @rtype: any
        """
        return self.__resourceContent

    def _set_resourceContent(self, value):
        """Set resource content
        @param value: content
        @type value: any
        """
        self.__resourceContent = value   

    resourceContent = property(_get_resourceContent, _set_resourceContent, None, 
                               "Resource content")