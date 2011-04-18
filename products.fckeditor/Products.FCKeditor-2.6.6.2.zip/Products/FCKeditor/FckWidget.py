from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import RichWidget, StringWidget
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.utils import base_hasattr

from utils import fckDefaultToolbar,  fckDefaultKeystrokes, fckDefaultMenuStyles

class FckWidget(RichWidget):
    _properties = RichWidget._properties.copy()
    _properties.update({
        'macro' : "fckwidget",
        'helper_js': ('fckeditor.js', 'fck_plone.js', ),
        'width'  : '100%',
        'height'  : '360px',
        'rows'  : 25,      #rows of TextArea if FCK is not available
        'cols'  : 80,      #same for cols
        'format': 1,
        'allow_content_upload': True, # called allow_file_upload in rich widget to allow html content upload
        'start_expanded': True, # set to False can be very useful when content type has more than 10 rich text fields ...      
        'allow_link_byuid': 1,
        'allow_relative_links': 1,
        'allow_latin_entities': 0,
        'force_paste_as_text' : 0,
        'keyboard_entermode' : 'p', #could be 'br' or 'div' for retturn mode
        'keyboard_shiftentermode': 'br', #the same for shift+return
        'keyboard_keystrokesmode': 'standard', #could be 'custom'
        'keyboard_customkeystrokes': fckDefaultKeystrokes(), #if precedent is custom
        'spellchecker' : 'ieSpell', # could be 'SpellerPages' (ieSpell = local spellchecker for FireFox and IE) or SpellerPages (complex: need an url)
        'fck_force_width' :  None, # not used in widget, choose a width
        'fck_force_height' :  None, #not used in widget, choose an height
        'fck_toolbar' :  'PloneDefaultToolbar', # could be 'FullToolBar' 'Basic' or 'Custom'
        'fck_custom_toolbar' : fckDefaultToolbar(), # toolbar could be customized if fck_toolbar is set to 'Custom'
        'allow_server_browsing' : 1,
        'allow_file_upload' : 1,
        'allow_image_upload' : 1,
        'allow_flash_upload' : 1,
        'file_portal_type' : 'File', #portal_type for file upload
        'image_portal_type' : 'Image', #portal_type for Image upload
        'browse_images_portal_types' : ['Image','ATPhoto','ATImage',], #portal_types for Images browsing
        'flash_portal_type' : 'File', #portal_type for Flash animation upload
        'browse_flashs_portal_types' : ['File','ATFile','PloneExFile',], #portal_types for Flash browsing
        'folder_portal_type' : 'Folder', #portal_type for Folder creation
        'pa_meta_types' : ['PloneArticle',], #portal_type for browsing inside PloneArticle types
        'rd_portal_types' : ['RichDocument', 'RichPage',], #portal_type for browsing inside RichDocument types
        'fck_area_style' : [], #a css to replace standard plone css inside editor area
        'fck_area_css_id' : 'content' , # the css id for css area, by default content
        'fck_area_css_class' : 'documentContent', # the css class applied for css area by default documentContent
        'fck_force_path' : 0, #set to 1 to force browser path to member personnal folder
        'fck_force_other_path' : '', # to force browser path to specific folder's id
        'fck_force_other_path_method' : '', # to force browser path with a specific method
        'fck_force_root' : 0, # set to 1 to force browser root to member personnal folder
        'fck_force_other_root' : '', # to force browser root to specific folder's id
        'fck_force_other_root_method' : '', # to force browser root with specific method
        'fck_default_skin' : 'default', #choose between 'default','silver','office2003'
        'fck_menu_styles' : fckDefaultMenuStyles(), #choose between 'default','silver','office2003'
        'fck_default_r2l' : 0, #default edition from right to left
        'fck_unpublished_states': ['visible','pending','rejected', 'waitreview'], # states which need to be hidden in browser even when user has view permission
        'fck_unpublished_view_roles': ['Manager','Reviewer','Owner', 'Contributor'], # roles allowed to view unpublished contents 
        })

    security = ClassSecurityInfo()
    
    security.declarePrivate ('paramsTuple')
    def _paramsTuple (self, instance, ):
        """ Returns editor skin, style,  and editor browser path & root
            depending on widget params & member prefs
        """    
        request = instance.REQUEST
        portal = instance.portal_url.getPortalObject()
        portal_url = instance.portal_url()
        server_url = request.get('SERVER_URL')
        member = portal.portal_membership.getAuthenticatedMember()        
        # editor skin
        member_fck_skin = member.getProperty('fck_skin','')
        fck_default_skin = getattr(self, 'fck_default_skin', 'default')
        fck_skin = member_fck_skin and member_fck_skin or fck_default_skin
        # find browser's path & root
        if portal.portal_membership.getHomeFolder() is not None :
            member_path = portal.portal_membership.getHomeUrl()
            if member_path:
                member_path=member_path.replace(portal_url, '')
        else :
            member_path=''        
        member_fck_path = member.getProperty('fck_path','')
        member_fck_root = member.getProperty('fck_root','')
        fck_force_path = getattr(self, 'fck_force_path', '')
        fck_force_other_path = getattr(self, 'fck_force_other_path', '')
        fck_force_other_path_method = getattr(self, 'fck_force_other_path_method', '')
        fck_force_root = getattr(self, 'fck_force_root', '')
        fck_force_other_root = getattr(self, 'fck_force_other_root', '')
        fck_force_other_root_method = getattr(self, 'fck_force_other_root_method', '')
        
        if fck_force_other_path_method and base_hasattr(instance, fck_force_other_path_method) :
            path_method = getattr(instance, fck_force_other_path_method)
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
        if fck_force_other_root_method and base_hasattr(instance, fck_force_other_root_method) :
            root_method = getattr(instance, fck_force_other_root_method)
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
        fck_default_style = instance.getFck_area_default_style()
        fck_area_style = getattr(self, 'fck_area_style', '')
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
        
        return (fck_skin, browser_path, browser_root, fck_style)
    
    security.declarePublic('fck_skin')
    def fck_skin (self, instance,):
        """ Returns editor skin
        """    
        return self._paramsTuple(instance,)[0]
      
    security.declarePublic('browser_path')
    def browser_path (self, instance ):
        """ Returns browser path
        """    
        return self._paramsTuple(instance,)[1]    
    
    security.declarePublic('browser_root')
    def browser_root (self, instance):
        """ Returns browser root
        """    
        return self._paramsTuple(instance)[2]    
    
    security.declarePublic('fck_style')
    def fck_style (self, instance, ):
        """ Returns editor skin
        """    
        return self._paramsTuple(instance)[3]
        
    security.declarePublic('getCustomConfig')
    def getCustomConfig (self, instance,):
        """ Returns editor custom js content
        """    
        start_expanded = getattr(self, 'start_expanded', True)
        fck_custom_toolbar = getattr(self, 'fck_custom_toolbar', '')
        keyboard_customkeystrokes = getattr(self, 'keyboard_customkeystrokes', '')
        fck_area_css_id = getattr(self, 'fck_area_css_id')
        fck_area_css_class = getattr(self, 'fck_area_css_class')
        fck_style = self.fck_style(instance)
        customConfig ="""FCKConfig.ToolbarStartExpanded	= %s;
        FCKConfig.ToolbarSets["Custom"] = %s ;
        FCKConfig.Keystrokes = %s ;
        FCKConfig.FontFormats = 'p;div;pre;code;address;h2;h3;h4;h5;h6' ;
        FCKConfig.StylesXmlPath = FCKConfig.EditorPath + 'fckstyles_plone.xml' ;
        FCKConfig.EditorAreaCSS		= %s ;
        FCKConfig.BodyId = '%s' ;
        FCKConfig.BodyClass = '%s' ;
        """  %(start_expanded and 'true' or 'false',
               fck_custom_toolbar,
               keyboard_customkeystrokes,
               fck_style,
               fck_area_css_id,
               fck_area_css_class)
        
        return customConfig      

    security.declarePublic('getBrowserValues')
    def getBrowserValues (self, instance,):
        """ Returns values for browsing/uploading
        """    
        browserDict = {}
        browserDict['fck_unpublished_states'] = self.fck_unpublished_states
        browserDict['fck_unpublished_view_roles'] = self.fck_unpublished_view_roles
        browserDict['allow_link_byuid'] = self.allow_link_byuid
        browserDict['allow_server_browsing'] = self.allow_server_browsing
        browserDict['allow_file_upload'] = self.allow_file_upload
        browserDict['allow_image_upload'] = self.allow_image_upload
        browserDict['allow_flash_upload'] = self.allow_flash_upload
        browserDict['file_portal_type'] = self.file_portal_type
        browserDict['image_portal_type'] = self.image_portal_type
        browserDict['flash_portal_type'] = self.flash_portal_type
        browserDict['pa_meta_types'] = self.pa_meta_types
        browserDict['rd_portal_types'] = self.rd_portal_types
        browserDict['folder_portal_type'] = self.folder_portal_type
        browserDict['browse_images_portal_types'] = self.browse_images_portal_types
        browserDict['browse_flashs_portal_types'] = self.browse_flashs_portal_types
        
        return browserDict      


registerWidget(FckWidget,
               title='FCKeditor Widget',
               description=('Renders a HTML widget that allows you to '
                            'type some content with FCKEditor, '
                            'choose formatting  and/or upload a file'),
               used_for=('Products.Archetypes.Field.TextField',)
               )
               

registerPropertyType('allow_content_upload', 'boolean', FckWidget)
registerPropertyType('start_expanded', 'boolean', FckWidget)
registerPropertyType('allow_relative_links', 'boolean', FckWidget)
registerPropertyType('force_paste_as_text', 'boolean', FckWidget)
registerPropertyType('allow_server_browsing', 'boolean', FckWidget)
registerPropertyType('allow_file_upload', 'boolean', FckWidget)
registerPropertyType('allow_image_upload', 'boolean', FckWidget) 
registerPropertyType('allow_flash_upload', 'boolean', FckWidget) 
registerPropertyType('fck_force_path', 'boolean', FckWidget)  
registerPropertyType('fck_force_root', 'boolean', FckWidget)  
registerPropertyType('fck_default_r2l', 'boolean', FckWidget)   
registerPropertyType('keyboard_entermode', 'string', FckWidget)
registerPropertyType('keyboard_shiftentermode', 'string', FckWidget)
registerPropertyType('keyboard_keystrokesmode', 'string', FckWidget)
registerPropertyType('spellchecker', 'string', FckWidget)
registerPropertyType('fck_force_width', 'string', FckWidget)
registerPropertyType('fck_force_height', 'string', FckWidget)
registerPropertyType('fck_toolbar', 'string', FckWidget)
registerPropertyType('file_portal_type', 'string', FckWidget)
registerPropertyType('image_portal_type', 'string', FckWidget)
registerPropertyType('flash_portal_type', 'string', FckWidget)
registerPropertyType('folder_portal_type', 'string', FckWidget)
registerPropertyType('fck_area_style', 'string', FckWidget)
registerPropertyType('fck_area_css_id', 'string', FckWidget)
registerPropertyType('fck_area_css_class', 'string', FckWidget)
registerPropertyType('fck_force_other_path', 'string', FckWidget)
registerPropertyType('fck_force_other_path_method', 'string', FckWidget)
registerPropertyType('fck_force_other_root', 'string', FckWidget)
registerPropertyType('fck_force_other_root_method', 'string', FckWidget)
registerPropertyType('fck_default_skin', 'string', FckWidget)
registerPropertyType('keyboard_customkeystrokes', 'text', FckWidget)
registerPropertyType('fck_custom_toolbar', 'text', FckWidget)
registerPropertyType('fck_menu_styles', 'text', FckWidget)
registerPropertyType('browse_images_portal_types', 'lines', FckWidget)
registerPropertyType('browse_flashs_portal_types', 'lines', FckWidget)
registerPropertyType('pa_meta_types', 'lines', FckWidget)
registerPropertyType('rd_portal_types', 'lines', FckWidget)
registerPropertyType('fck_unpublished_states', 'lines', FckWidget)
registerPropertyType('fck_unpublished_view_roles', 'lines', FckWidget)


# this widget can be used for browsing internal links
class FckLinkWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "fcklinkwidget",
        'helper_js': ('fck_link.js', ), 
        'internal_url_only': False, 
        'browser_root':'',
        'browser_path':'',
        })

    security = ClassSecurityInfo()
    
registerWidget(FckLinkWidget,
               title='FCKeditor Internal Links Widget',
               description=('Renders a string widget for links that allows you to '
                            'browse internal links on your site'),
               used_for=('Products.Archetypes.Field.TextField',)
               )
                   
