from collective.amberjack.core.utils import AmberjackTool

PROJECTNAME = "collective.amberjack.core"

tools = (
    AmberjackTool,
    )

def initialize(context):
    from Products.CMFCore import utils
    utils.ToolInit("%s Tool" % PROJECTNAME,
                   tools=tools,
                   icon="tool.gif",
                   ).initialize(context)
