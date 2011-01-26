## Script (Python) "prefs_fckeditor_member_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=set
##
try:
    from Products.CMFPlone.utils import transaction_note
except:
    from Products.CMFPlone import transaction_note

portal = context.portal_url.getPortalObject()

request = context.REQUEST

member=context.portal_membership.getAuthenticatedMember()
props = context.portal_properties.fckeditor_properties


fck_force_root=props.fck_force_root
fck_force_path=props.fck_force_path
fck_force_other_root=props.fck_force_other_root
fck_force_other_path=props.fck_force_other_path

if fck_force_root or fck_force_other_root :

    request.set('fck_root', '')

else :

    fck_root=request.get('fck_root','')
    fck_path=request.get('fck_path','')
    if fck_root :
        try :
            browser_root= portal.restrictedTraverse(fck_root.lstrip('/'))
        except:
            return request.RESPONSE.redirect(
                "%s/prefs_fckeditor_member?portal_status_message=%s"%(context.absolute_url(),"Error : The browser root don't exist"))

        if not fck_root in fck_path:
            request.set('fck_path', fck_root)


if fck_force_path or fck_force_other_path :

    request.set('fck_path', '')

else :    
   
    fck_root=request.get('fck_root','')
    if fck_path :
        try :
            browser_path=portal.restrictedTraverse(fck_path.lstrip('/'))
        except:
            return request.RESPONSE.redirect(
                "%s/prefs_fckeditor_member?portal_status_message=%s"%(context.absolute_url(),"Error : The browser opening folder path don't exist"))





member=context.portal_membership.getAuthenticatedMember()
member.setProperties(request)

tmsg=member.getUserName()+' personalized their settings.'
transaction_note(tmsg)

return request.RESPONSE.redirect(
    '%s/prefs_fckeditor_member?portal_status_message=%s'%(context.absolute_url(),'Your personal settings have been saved.'))
