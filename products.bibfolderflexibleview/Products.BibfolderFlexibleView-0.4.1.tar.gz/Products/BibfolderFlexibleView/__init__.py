from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils as CMFutils

from config import GLOBALS
from tool import flexview_tool

registerDirectory('skins', GLOBALS)

def initialize(context):
    CMFutils.ToolInit(
        'Bibliography Flexible View Tool',
        icon='bibliography_tool.png',
        tools=(flexview_tool.FlexviewTool,),
        ## product_name=PROJECTNAME,
        ).initialize(context)

