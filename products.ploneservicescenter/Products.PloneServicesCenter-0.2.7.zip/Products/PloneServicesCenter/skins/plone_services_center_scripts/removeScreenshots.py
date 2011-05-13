## Script (Python) "removeScreenshots"
##title=Cleanup ZODB screenshot images after moving to shrinktheweb.com
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

def removeScreenshot(obj, path):
    obj.setScreenshot("DELETE_IMAGE")

context.ZopeFindAndApply(
    context, obj_metatypes=('SiteUsingPlone', 'CaseStudy'),
    search_sub=True, apply_func=removeScreenshot)
