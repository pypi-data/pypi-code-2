## Script (Python) "bibflexview_get_ass_obs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=prop_src, REQUEST=None
##title=
##

if prop_src.pubentry_use_ao:
    ao_path = (prop_src.pubentry_ao_path != '') and prop_src.pubentry_ao_path or '/'.join(context.portal_url.getPortalObject().getPhysicalPath())
    
    req = {'path': ao_path, 'language': 'all'}
    if prop_src.ao_show_priv:
        ass_obs_raw = context.portal_catalog.search(req)
    else: ass_obs_raw = context.portal_catalog(req)
    #ass_obs_raw = context.portal_catalog(req)
    #ass_obs_raw = context.portal_catalog(path=ao_path, language='all')
    
    rts = context.portal_bibliography.getReferenceTypes()    
                    
    ass_obs_raw = [x for x in ass_obs_raw if x.portal_type not in rts]                  
    d = context.bibflexview_get_url_dict(prop_src, ass_obs_raw, REQUEST)
else:
    d = {}
        
return d
