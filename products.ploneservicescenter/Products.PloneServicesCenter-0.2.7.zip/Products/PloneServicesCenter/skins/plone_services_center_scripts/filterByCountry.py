## Script (Python) "filterByCountry"
##title=Helper method for country filter
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

request = container.REQUEST
try:
    country = request.country[0]
    request.response.redirect(country)
except:
    pass
 
