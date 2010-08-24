import sys
from AccessControl import ClassSecurityInfo
try:
    from App.class_init import InitializeClass
except ImportError:
    # Zope 2.9
    from Globals import InitializeClass
from Products.CMFCore import utils as cmf_utils

this_module = sys.modules[ __name__ ]
 
product_globals = globals()

import beatbox.python_client
import salesforcebaseconnector
tools = ( salesforcebaseconnector.SalesforceBaseConnector,
          )

def initialize(context):
    cmf_utils.ToolInit('Salesforce Base Connector',
                    tools = tools,
                    icon='www/salesforce.png'
                    ).initialize( context )

    # initialize security for the QueryResult and QueryRecordSet classes from beatbox
    beatbox.python_client.QueryRecord.security = security = ClassSecurityInfo()
    beatbox.python_client.QueryRecord.__allow_access_to_unprotected_subobjects__ = 1
    security.declareObjectPublic()
    InitializeClass(beatbox.python_client.QueryRecord)
    beatbox.python_client.QueryRecordSet.security = security = ClassSecurityInfo()
    beatbox.python_client.QueryRecordSet.__allow_access_to_unprotected_subobjects__ = 1
    security.declareObjectPublic()
    InitializeClass(beatbox.python_client.QueryRecordSet)