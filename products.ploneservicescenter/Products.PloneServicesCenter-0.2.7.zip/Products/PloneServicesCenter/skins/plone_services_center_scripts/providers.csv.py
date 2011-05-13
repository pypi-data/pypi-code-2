## Script (Python) "Providrs CSV export"
##title=Helper method for country filter
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

providers = context.getProviders()

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/csv')

from Products.CMFCore.utils import getToolByName
workflow_tool = getToolByName(context, 'portal_workflow')

# header row
print '"Provider name","Provider contact name","Provider contact email","Sponsorship","Premium sponsorship","Firm size","Workflow state"'

for provider_brain in providers:
    provider = provider_brain.getObject()
    wfstate = workflow_tool.getInfoFor(provider, 'review_state', '')

    print '"%s","%s","%s","%s","%s","%s","%s",' % (provider.pretty_title_or_id(), provider.getContactName(), provider.getContactEmail(), provider.isSponsor(), provider.isPremium(), provider.getEmployees(), wfstate )
    
return printed
 
