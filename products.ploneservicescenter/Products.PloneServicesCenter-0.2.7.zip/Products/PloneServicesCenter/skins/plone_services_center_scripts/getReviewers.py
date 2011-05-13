## Script (Python) "getReviewers"
##title=Return members of the "Reviewers" group
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

from Products.CMFCore.utils import getToolByName

tool = getToolByName(context, 'portal_groups')
group = tool.getGroupById('Reviewers')
if group is None:
    return ()
return group.getGroupMembers()
