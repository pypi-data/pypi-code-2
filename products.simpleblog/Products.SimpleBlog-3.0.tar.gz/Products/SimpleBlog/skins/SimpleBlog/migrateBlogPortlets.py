## Script (Python) "migrateBlogPortlets"
##title=Migrate blog portlets from old to new type
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

context.simpleblog_tool.migrateBlogPortlets()
return "Migration completed" 