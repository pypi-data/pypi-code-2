##parameters=compopage_path, target_path, target_index
portal = context.portal_url.getPortalObject()

# First we create the composite Element
destination = portal.restrictedTraverse(target_path)
factory = destination.manage_addProduct['CompositePack'].manage_addElement
compo = portal.restrictedTraverse(compopage_path)
new_id = compo.cp_container.generateUniqueIdForCSS()
new_id = factory(id=new_id)
destination.moveObjectToPosition(new_id, int(target_index))
new_el = getattr(destination, new_id)

#Second we create our internal object that contains the content
factory = compo.cp_container.titles.manage_addProduct['CompositePack'].manage_addPortlet
new_id = context.generateUniqueId()
new_id = factory(id=new_id)
new_fragment = getattr(compo.cp_container.titles, new_id)
new_fragment.setComposite(new_el.UID())

# Finally we set the composite elements' target to our newly created content item.
uid = new_fragment.UID()
new_el.setTarget(uid)

pageDesignUrl = compo.absolute_url() + '/design_view'

return context.REQUEST.RESPONSE.redirect(pageDesignUrl)
