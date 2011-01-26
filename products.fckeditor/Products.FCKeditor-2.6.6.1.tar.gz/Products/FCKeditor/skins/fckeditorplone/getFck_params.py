## Script (Python) "getFck_params"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.FCKeditor.utils import fckDefaultKeystrokes
from Products.CMFPlone.utils import base_hasattr

request=context.REQUEST
portal=context.portal_url.getPortalObject()
portal_url=context.portal_url()
server_url=request.get('SERVER_URL')
member=portal.portal_membership.getAuthenticatedMember()
fckProps=portal.portal_properties.fckeditor_properties



# current fck skin
member_fck_skin = member.getProperty('fck_skin','')
fck_default_skin = fckProps.fck_default_skin
fck_skin=test(member_fck_skin, member_fck_skin, fck_default_skin)

# path et root du browser
if portal.portal_membership.getHomeFolder() is not None :
   member_path = portal.portal_membership.getHomeUrl()
   if member_path:
       member_path=member_path.replace(portal_url, '')
else :
   member_path=''
member_fck_path = member.getProperty('fck_path','')
member_fck_root = member.getProperty('fck_root','')
fck_force_path = fckProps.fck_force_path
fck_force_other_path = fckProps.fck_force_other_path
fck_force_root = fckProps.fck_force_root
fck_force_other_root = fckProps.fck_force_other_root
fck_force_other_path_method = fckProps.fck_force_other_path_method
fck_force_other_root_method = fckProps.fck_force_other_root_method
     
     
if fck_force_other_path_method and base_hasattr(context, fck_force_other_path_method) :
    path_method = getattr(context, fck_force_other_path_method)
    if callable(path_method):
        browser_path = path_method()
    else :
        browser_path = path_method
else :            
    if fck_force_path :
         browser_path = member_path
    elif fck_force_other_path :
         browser_path= fck_force_other_path
    elif member_fck_path :
         browser_path= member_fck_path
    else :
         browser_path=''

if fck_force_other_root_method and base_hasattr(context, fck_force_other_root_method) :
    root_method = getattr(context, fck_force_other_root_method)
    if callable(root_method):
        browser_root = root_method()
    else :
        browser_root = root_method
else : 
    if fck_force_root :
         browser_root = member_path
    elif fck_force_other_root :
         browser_root= fck_force_other_root
    elif member_fck_root :
         browser_root= member_fck_root
    else :
         browser_root=''

# editor area style
# by default plone.css or ploneStylexxx.css with portal_css (plone 2.1.x)
fck_default_style = context.getFck_area_default_style()
fck_area_style = fckProps.fck_area_style
if len(fck_area_style):
    i = 0
    fck_style= "["
    for css in fck_area_style :
       i += 1
       if css.startswith('http') :
          fck_style+="'%s'" %css
       else :
          fck_style.lstrip('/')
          fck_style+="'%s/%s'" %(portal_url, css)      

       # IE javascript do not support "," at the end of js lists
       if i< len(fck_area_style) :
          fck_style+=", "
    
    fck_style += "]"
else :
    fck_style = fck_default_style


start_expanded = fckProps.start_expanded
allow_link_byuid = fckProps.allow_link_byuid
allow_relative_links = fckProps.allow_relative_links
spellchecker = fckProps.spellchecker
allow_latin_entities = fckProps.allow_latin_entities
force_paste_as_text = fckProps.force_paste_as_text
keyboard_entermode = fckProps.keyboard_entermode
keyboard_shiftentermode = fckProps.keyboard_shiftentermode
keyboard_keystrokesmode = fckProps.keyboard_keystrokesmode
if keyboard_keystrokesmode=='standard':
   keyboard_customkeystrokes = fckDefaultKeystrokes()
else:   
   keyboard_customkeystrokes = fckProps.keyboard_customkeystrokes
fck_toolbar = fckProps.fck_toolbar
fck_custom_toolbar = fckProps.fck_custom_toolbar
fck_force_width = fckProps.fck_force_width
fck_force_height = fckProps.fck_force_height
allow_server_browsing = fckProps.allow_server_browsing
allow_file_upload = fckProps.allow_file_upload
allow_image_upload = fckProps.allow_image_upload
allow_flash_upload = fckProps.allow_flash_upload
file_portal_type = fckProps.file_portal_type
folder_portal_type = fckProps.folder_portal_type
image_portal_type = fckProps.image_portal_type
folder_portal_type = fckProps.folder_portal_type
browse_images_portal_types = fckProps.browse_images_portal_types
flash_portal_type = fckProps.flash_portal_type
browse_flashs_portal_types = fckProps.browse_flashs_portal_types
pa_meta_types = fckProps.pa_meta_types
rd_portal_types = fckProps.rd_portal_types or ['RichDocument', 'RichPage'] #need to add it in configlet form
fck_default_r2l = fckProps.fck_default_r2l
fck_unpublished_states = fckProps.fck_unpublished_states
if not fck_unpublished_states:
    fck_unpublished_states = ('noSpecificState',)
fck_unpublished_view_roles = fckProps.fck_unpublished_view_roles
if not fck_unpublished_view_roles:
    fck_unpublished_states = ('noSpecificRole',)
fck_menu_styles = fckProps.fck_menu_styles


fckParams = {'fck_skin':fck_skin, 
             'fck_style':fck_style, 
             'browser_path':browser_path, 
             'browser_root':browser_root,
             'fck_menu_styles':fck_menu_styles,
             'allow_link_byuid':allow_link_byuid,
             'start_expanded':start_expanded,
             'allow_latin_entities':allow_latin_entities,
             'allow_relative_links':allow_relative_links,
             'force_paste_as_text':force_paste_as_text,
             'keyboard_entermode':keyboard_entermode,
             'keyboard_shiftentermode':keyboard_shiftentermode,
             'keyboard_keystrokesmode':keyboard_keystrokesmode,
             'keyboard_customkeystrokes':keyboard_customkeystrokes,
             'spellchecker':spellchecker,
             'fck_toolbar':fck_toolbar,
             'fck_custom_toolbar':fck_custom_toolbar,
             'fck_force_width':fck_force_width,
             'fck_force_height':fck_force_height,
             'force_paste_as_text':force_paste_as_text,
             'allow_server_browsing':allow_server_browsing,
             'allow_file_upload':allow_file_upload,
             'allow_image_upload':allow_image_upload,
             'allow_flash_upload':allow_flash_upload ,
             'file_portal_type':file_portal_type ,
             'folder_portal_type':folder_portal_type ,
             'image_portal_type':image_portal_type ,
             'browse_images_portal_types':browse_images_portal_types,
             'flash_portal_type':flash_portal_type,
             'browse_flashs_portal_types':browse_flashs_portal_types,
             'fck_default_r2l':fck_default_r2l,
             'pa_meta_types': pa_meta_types,
             'rd_portal_types':rd_portal_types,
             'fck_unpublished_states':list(fck_unpublished_states),
             'fck_unpublished_view_roles':list(fck_unpublished_view_roles) }

return fckParams
