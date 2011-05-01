## Script (Python) "edit_compo_element"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote

action_tool = getToolByName(context, 'portal_actions')
content = context.dereference()
valid_actions = action_tool.listFilteredActionsFor(content)

# Get the edit action if it is valid, otherwise fall back to view
# If all else fails just use the url.
object_actions = valid_actions.get('object', [])

action = None
for id in ('edit', 'view'):
    for a in object_actions:
        if a.get('id', None)==id:
            action = a['url']
            context.REQUEST.RESPONSE.redirect(action)
            return
            
# No suitable action found, just go to the url
context.REQUEST.RESPONSE.redirect(content.absolute_url())
