from Products.CMFCore import utils

from collective.arboreal.arboreal import Arboreal
from collective.arboreal.config import *


def initialize(context):
    # initialize tree management tool
    utils.ToolInit(TOOL_NAME,
                   tools=[Arboreal],
                   icon='arboreal.gif').initialize( context )

    # Import the multipath index so it is registered
    import index
    import arborealselection 
    context.registerClass(index.MultiPathIndex,
        permission='Add Pluggable Index',
        constructors=(index.manage_addMultiPathIndexForm,
                      index.manage_addMultiPathIndex),
        icon='zmi/index.gif',
        visibility=None
     )
