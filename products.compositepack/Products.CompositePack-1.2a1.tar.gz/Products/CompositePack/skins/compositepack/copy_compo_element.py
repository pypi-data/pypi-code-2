content = context.dereference()

if 0:
 print "content=",content
 print "container=",content.aq_parent
 print "id=",content.getId()
 return printed

compo = content.aq_inner.parent
pageDesignUrl = compo.absolute_url() + '/design_view'

content.aq_parent.manage_copyObjects([content.getId()], REQUEST=context.REQUEST)
return context.REQUEST.RESPONSE.redirect(pageDesignUrl)
