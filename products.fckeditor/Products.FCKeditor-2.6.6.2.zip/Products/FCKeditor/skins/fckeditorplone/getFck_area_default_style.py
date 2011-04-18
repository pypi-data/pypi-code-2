## Script (Python) "getFck_area_default_style"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.PythonScripts.standard import url_quote
Portal=context.portal_url.getPortalObject()
portal_root=Portal.absolute_url()
# render css js List in a string
css_jsList="["

current_skin= context.getCurrentSkinName()
skinname = url_quote(current_skin)
css_res=container.portal_css.getEvaluatedResources(context)
for css in css_res :
   if css.getMedia() not in ('print', 'projection') and css.getRel()=='stylesheet' :
     cssPloneId = css.getId()
     cssPlone= '%s/portal_css/%s/%s' %(portal_root, skinname, cssPloneId)
     css_jsList += "'%s', " %cssPlone  


css_jsList += "'%s/fck_ploneeditorarea.css']" %portal_root  

return css_jsList
