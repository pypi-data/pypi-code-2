## Script (Python) "verkkomaksutnotify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Verkkomaksut Notify
##


#from Products.PythonScripts.standard import html_quote
#request = container.REQUEST
#RESPONSE =  request.RESPONSE

## Return a string identifying this script.
#print "This is the", script.meta_type, '"%s"' % script.getId(),
#if script.title:
#    print "(%s)" % html_quote(script.title),
#print "in", container.absolute_url()
#return printed
#from Products.CMFCore.utils import getToolByName

request = container.REQUEST
#response = request.RESPONSE
#portal_url = getToolByName(container, 'portal_url')
#portal_url = container.portal_url
print request
return printed
#url = '%s/verkkomaksut-thanks' %container.absolulte_url()

#return response.redirect(url)
