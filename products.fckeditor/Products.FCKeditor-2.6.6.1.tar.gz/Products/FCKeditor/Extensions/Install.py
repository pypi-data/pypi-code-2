###
# FCKEditor2-Installer-Script
# 
###

from Products.FCKeditor import config
from Products.FCKeditor.config import *
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import AcceleratedHTTPCacheManager
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from types import InstanceType

# To install fck demo types
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.Extensions.utils import installTypes             
                  


# add FCK HTTPCache
# editor cached for all users 7 days
def install_cache(self, out):

 if 'FckHTTPCache' not in self.objectIds():
      self._setObject('FckHTTPCache',AcceleratedHTTPCacheManager('FckHTTPCache'))
      cache_settings={'anonymous_only': 0,  'notify_urls': (), 'interval': FCKHTTPCACHE_DURATION } 
      self.FckHTTPCache.manage_editProps('FCK Http Cache', settings=cache_settings)
      print >>out, "Added FCKeditor HTTP Cache"


def install_demo_types(self, out):

    typeInfo = listTypes(PROJECTNAME)
    installTypes(self, out, typeInfo, PROJECTNAME)  
    print >> out, "Successfully installed FCK Editor Demo Content Types."
    

def install_plone_resources(self, out):

    # Register js
    jsTool = getToolByName(self, 'portal_javascripts', None)
    for id, kwargs in FCK_JSCRIPTS:
         jsTool.registerScript(id, **kwargs)  
    print >> out, 'Javascripts installed'  
    
    # Register kss for inline editing
    kssTool = getToolByName(self, 'portal_kss', None)
    if kssTool is not None :
        for id, kwargs in FCK_KSS:
             kssTool.registerKineticStylesheet(id, **kwargs)  
        print >> out, 'Kss files installed'      
    # without kss we must init fck onload
    else :
        jsTool.registerScript('fck_ploneInit.js', enabled = True,
                                                  cookable = True,
                                                  compression = 'safe',
                                                  cacheable = True)
        print >> out, 'fck_ploneInit.js installed' 


    
def uninstall_plone_resources(self, out):

    # Unregister js
    jsTool = getToolByName(self, 'portal_javascripts', None)
    for id in FCK_JSCRIPTS:
         jsTool.manage_removeScript(id)  
    print >> out, 'Javascripts removed'      
    
    # Unregister kss
    kssTool = getToolByName(self, 'portal_kss', None)
    if kssTool is not None :
        for id, kwargs in FCK_KSS:
             kssTool.manage_removeKineticStylesheet(id)  
        print >> out, 'Kss files removed'      


def install_plone(self, out):
    """ add FCK Editor to 'my preferences' """
    portal_props=getToolByName(self,'portal_properties')
    site_props=getattr(portal_props,'site_properties', None)
    attrname='available_editors'
    if site_props is not None:
        editors=list(site_props.getProperty(attrname)) 
        if 'FCKeditor' not in editors:
           editors.append('FCKeditor')
        if 'FCK Editor' in editors:
           editors.remove('FCK Editor')
        site_props._updateProperty(attrname, editors)        
        print >>out, "Added FCKeditor.Plone %s to available editors in Plone." %PRODUCT_VERSION
    portal = getToolByName(self, 'portal_url').getPortalObject()
    try:
        portal.portal_controlpanel.registerConfiglet(**fckeditor_configlet)
        print >>out, "Added FCKeditor.Plone %s configlet in Plone Control Panel." %PRODUCT_VERSION
    except:
        pass

    try:
        portal.portal_controlpanel.registerConfiglet(**fckeditor_member_prefs)
        print >>out, "Added FCKeditor member preferences in Plone Control Panel."
    except:
        pass    
    install_global_properties(self, out)
    install_member_properties(self, out)
    install_plone_resources(self, out)



def install_member_properties(self, out):
    mdtool = getToolByName(self, 'portal_memberdata')
    for prop, tp, val in config.memberData_properties:
        if not mdtool.hasProperty(prop):
            mdtool._setProperty(prop, val, tp)

    print >> out, "Successfully installed FCK Editor member properties."


def install_global_properties(self, out):
    # install fckeditor global properties 
    # or update old fckeditor properties
    if not hasattr(self.portal_properties, 'fckeditor_properties'):
        self.portal_properties.addPropertySheet(
            'fckeditor_properties', 'FCK Editor properties')
    
    props = self.portal_properties.fckeditor_properties 
    pIds = props.propertyIds()       

    for prop, tp, val in config.fckeditor_properties:
        if not prop in pIds :
            #props._setProperty(prop, val, tp)
            props.manage_addProperty(prop, val, tp)
        elif props.getPropertyType(prop) != tp :  
            props.manage_delProperties([prop])
            props.manage_addProperty(prop, val, tp)  
        elif prop in UPDATE_PROPERTIES:
            props.manage_changeProperties({prop: val})    
            

    print >> out, "Successfully installed FCK Editor global properties."


def install_subskin(self, out, skin_name, globals=GLOBALS):
    skinstool=getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', globals)

    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName) 
        path = [i.strip() for i in  path.split(',')]
        try:
            if skin_name not in path:
                path.insert(path.index('custom') +1, skin_name)
        except ValueError:
            if skin_name not in path:
                path.append(skin_name)  

        path = ','.join(path)
        skinstool.addSkinSelection( skinName, path)

# Copyright: quintagroup.com (from qPloneResolveUID)

def registerTransform(self, out, name, module):
    transforms = getToolByName(self, 'portal_transforms')
    try:
        transforms.manage_addTransform(name, module)
        print >> out, "Registered transform", name
    except:
        print >> out, "Could not register transform", name   

def registerTransformPolicy(self, out, output_mimetype, required_transforms):
    transforms = getToolByName(self, 'portal_transforms')
    try :
        transforms.manage_addPolicy(output_mimetype, required_transforms)
        print >> out, "Registered policy for %s mimetype" %output_mimetype
    except :    
        print >> out, "could not register policy for %s mimetype" %output_mimetype
    
def unregisterTransform(self, out, name):
    transforms = getToolByName(self, 'portal_transforms')
    try:
        transforms.unregisterTransform(name)
        print >> out, "Removed transform", name
    except:
        print >> out, "Could not remove transform", name, "(not found)"

def unregisterTransformPolicy(self, out, output_mimetypes):
    transforms = getToolByName(self, 'portal_transforms')
    try:
        transforms.manage_delPolicies(output_mimetypes)
        print >> out, "Removed transform policy for %s mimetype" %output_mimetypes
    except:
        print >> out, "could not remove transform policy for %s mimetype" %output_mimetypes


def install(self):
    out = StringIO()
    print >>out, "Installing FCKeditor %s in your site" %PRODUCT_VERSION
    
    if INSTALL_DEMO_TYPES :
        install_demo_types(self, out)
    
    # no more used (use CacheFu or change your httpcache params)
    #install_cache(self, out)

    # plone specific installation
    try:
        import Products.CMFPlone
    except ImportError:
        pass
    else:
        install_plone(self, out)

    for layer in SKIN_LAYERS :
        install_subskin(self, out, layer)
        
    print >> out, "Installing fck_ruid_to_url transform"
    registerTransform(self, out, 'fck_ruid_to_url', 'Products.FCKeditor.transforms.fck_ruid_to_url')
    
    print >> out, "Installing transform policy for %s mimetype" %DOCUMENT_DEFAULT_OUTPUT_TYPE
    registerTransformPolicy(self, out, DOCUMENT_DEFAULT_OUTPUT_TYPE, REQUIRED_TRANSFORM)        

    print >>out, "FCKeditor %s installation done." %PRODUCT_VERSION
    
    return out.getvalue()


def uninstall(self):
    out = StringIO()
    
    # remove configlet from plone control panel
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        configTool.unregisterConfiglet('fckeditor_configlet')
        out.write('FCK Editor Configlet removed from Plone Control Panel\n')
        configTool.unregisterConfiglet('fckeditor_member_prefs')
        out.write('FCK Editor Member Preferences removed from Plone Control Panel\n')
    
    unregisterTransform(self, out, 'fck_ruid_to_url')
    
    print >> out, "Removing transform policy for %s mimetype" %DOCUMENT_DEFAULT_OUTPUT_TYPE
    unregisterTransformPolicy(self, out, [DOCUMENT_DEFAULT_OUTPUT_TYPE,]) 
    
    uninstall_plone_resources(self, out)       
