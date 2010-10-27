from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.utils import ToolInit
from Products.SimpleBlog.config import PROJECTNAME
from Products.SimpleBlog.Permissions import wireAddPermissions

# Module aliases - we don't always get it right on the first try, but and we
# can't move modules around because things are stored in the ZODB with the
# full module path. However, we can create aliases for backwards compatability.

from Products.SimpleBlog import content
import sys
sys.modules['Products.SimpleBlog.Blog'] = content.blog
sys.modules['Products.SimpleBlog.BlogEntry'] = content.blogentry
sys.modules['Products.SimpleBlog.BlogFolder'] = content.blogfolder

def initialize(context):
    from Products.SimpleBlog.content import BlogEntry
    from Products.SimpleBlog.content import Blog
    from Products.SimpleBlog.content import BlogFolder


    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)

    from Products.SimpleBlog.Permissions import permissions
    
    allTypes = zip(content_types, constructors)
    wireAddPermissions()
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.__name__)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.__name__],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

        
    from SimpleBlogTool import SimpleBlogManager
    utils.ToolInit(
        'SimpleBlog manager', 
        tools=(SimpleBlogTool.SimpleBlogManager,),  
        icon='tool.gif', ).initialize(context)

