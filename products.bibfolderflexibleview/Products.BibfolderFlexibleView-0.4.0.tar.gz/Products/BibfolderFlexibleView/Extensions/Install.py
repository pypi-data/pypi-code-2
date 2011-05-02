from cStringIO import StringIO

from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

import string

from Products.BibfolderFlexibleView.config import *
from Acquisition import aq_base

# skins registrieren. geklaut von FolderMapView
skin_names = ('BibfolderFlexibleView',)
def setupSkin(self, out):
    skinsTool = getToolByName(self, 'portal_skins')
    
    # Add directory views
    try:  
        addDirectoryViews(skinsTool, 'skins', GLOBALS)
        out.write( "Added directory views to portal_skins.\n" )
    except:
        out.write( '*** Unable to add directory views to portal_skins.\n')

    # Go through the skin configurations and insert the skin
    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        changed = 0
        for skin_name in skin_names:
            if skin_name not in path:
                try: 
                    path.insert(path.index('custom')+1, skin_name)
                    changed = 1
                except ValueError:
                    path.append(skin_name)
                    changed = 1

        if changed:        
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinsTool.addSkinSelection(skin, path)
            out.write("Added %s to %s skin\n" % (', '.join(skin_names),skin))
        else:
            out.write("Skipping %s skin, %s already set up\n" % (skin, ', '.join(skin_names)))

# teile dem portal_types tool mit, welche views wir fuer welche typen hinzufuegen moechten 
# auch geklaut aus FolderMapView           
def setupDisplayViews(self, out, dict):
    tool = getToolByName(self, 'portal_types')
    for pt, views in dict.items():
        try:
            FTI = getattr(tool, pt)
            nviews = FTI.view_methods
            for view in views:
                if view not in nviews:
                    nviews += (view,)
            
            for view in views:
                if view not in nviews:
                    try: 
                        nviews.insert(0, view)
                    except ValueError:
                        nviews.append(view)
        
            FTI.view_methods = nviews
            print >> out, "Registered display views for %s in portal_types." % pt
        except AttributeError:
            if pt == 'BibliographyFolder':
                raise "Can't find the BibliographyFolder type. Is CMFBibliographyAT installed?\n"
            else:
                out.write('Could not find %s type, skipping set up of views for that type. Once you install a product providing this type, be sure to reinstall BibfolderFlexibleView for full functionality\n' % pt)
                pass 

# entferne alle views, fuer die wir verantwortlich sind
def removeDisplayView(self, out, dict):
    tool = getToolByName(self, 'portal_types')
    for ptype, vs in dict.items():
        try:
            p = getattr(tool, ptype)
            views = list(p.view_methods)
            for v in vs:
                if v in views:
                    views.remove(v)
            p.view_methods = tuple(views)
        except AttributeError:
            pass
            
# code inspiriert von CMFBibliographyAT
# TODO: ueber sinn und unsinn der benennung nachdenken        
def setupTool(self, out):
    if hasattr(self, 'portal_bibliography_flexible_view'):
        self.manage_delObjects(['portal_bibliography_flexible_view'])
        out.write('Deleting old tool; make sure you repeat customizations.')
    out.write(PROJECTNAME)
    addTool = self.manage_addProduct[PROJECTNAME].manage_addTool
    addTool('Bibliography Flexible View Tool', None)
    out.write("\nAdded the bibliography flexible view tool to the portal root folder.\n")
    mytool = getToolByName(self, 'portal_bibliography_flexible_view')
    mytool.__post_init__()

# wenn es Bibfolder gibt, bei denen eine alte version dieser ansicht
# schon genutzt wurde, koennte es noetig sein, deren properties - sofern
# wir die schon mal angefasst haben - auf den neusten stand zu bringen    
def updateBibFolderProperties(self, out):
    cat = getToolByName(self, 'portal_catalog')
    our_tool = getToolByName(self, 'portal_bibliography_flexible_view')
    bfs = cat(portal_type=BIBFOLDERLIKE_TYPES, Language='all')
    bfs = [x.getObject() for x in bfs if x.getObject()]
    for bf in bfs:
        # pubentry_ao_mask ist unser (willkuerliches) signal zum eingreifen
        if bf.hasProperty('pubentry_ao_mask'):
            out.write("%s already has BibFlexView config properties, updating\n" % bf.id)
            our_tool.copy_tool_properties(bf, force_it=True)
	    bf.setLayout('bibfolder_flexible_view')

# wenn wir bei nem Bibfolder properties angelegt haben, loesch sie
def removeBibFolderProperties(self, out):
    cat = getToolByName(self, 'portal_catalog')
    our_tool = getToolByName(self, 'portal_bibliography_flexible_view')
    bfs = cat(portal_type=BIBFOLDERLIKE_TYPES, Language='all')
    bfs = [x.getObject() for x in bfs if x.getObject()]
    for bf in bfs:
        # pubentry_ao_mask ist unser (willkuerliches) signal zum eingreifen
        if bf.hasProperty('pubentry_ao_mask'):
            out.write("removing config properties set in %s\n" % bf.id) 
            for p in our_tool.propertyMap():
                if bf.hasProperty(p['id']) and p['id'] != 'title': 
                    bf.manage_delProperties([p['id']])

# zusaetzlich gewuenschte felder zum katalog hinzufuegen                    
def addCatalogMetadata(self, out):
    cat = getToolByName(self, 'portal_catalog')
    for m in CATALOG_METADATA_ENTRIES:
        if not m in cat.schema():
            cat.addColumn(m)
            out.write('added %s to catalog metadata\n' % m)
            out.write('*** you might want to do a catalog update if you already have bibliographical references catalogued ***\n')
        else: 
            out.write('%s already in catalog metadata\n' % m)

# wir verzichten natuerlich auf ein revmoveCatalogMetadata, kann ja sein, dass 
# sich inzwischen schon andere darauf verlassen

# mehr oder weniger kopiert von bibliography
def addPrefsPanel(self, out):
    cp=getToolByName(self, 'portal_controlpanel', None)
    if not cp:
        out.write("No control panel found. Skipping installation of the setup panel.\n")
    else:
 	cp.addAction(id='BibFlexViewSetup',
                     name='Bibfolder Flexible View Setup',
                     action='string:${portal_url}/bibflexview_prefs_form',
                     permission='Manage portal',
                     category='Products',
                     appId='BibfolderFlexibleView',
                     imageUrl='bibliography_tool.png',
                     description='Configure global settings of the flexible Bibfolder view')
        out.write("Installed the bibflexview tool configuration panel.\n")

def removePrefsPanel(self):
    cp=getToolByName(self, 'portal_controlpanel', None)
    if cp:
        cp.unregisterApplication('BibfolderFlexibleView')   

# falls noch wo ne von uns ueberschriebene export-action uebrig ist, rueckgaengig machen        
def removeAction(self, out):
    """
    removes the export action from the actions tool
    (why doesn't the quickinstaller do that?)
    """
    acttool = getToolByName(self, 'portal_actions')
    actions = list(acttool._actions)
    keep = []
    for a in actions:
        if a.id != 'exportBib' or a.action.text != 'string:${object_url}/bibliography_flex_exportForm':
            keep.append(a)
            #out.write("a.id %s a.action %s \n" % (a.id, a.action.text))
            #out.write("keeping action %s \n" % a.id)
    acttool._actions = tuple(keep)
    if actions != keep:
        return True
    return False

def undoMyActions(self, out):
    if not removeAction(self, out):
        return
    ap=getToolByName(self, 'portal_actions')

    # Add exportBib action to the actions tool
    ## rr: this is still the old way, i.e., name instead of title;
    ## no support for description; permission instead of permissions;
    ## we ought to move to an extension
    ## profile anyway soon so I don't care; it works for now
    ap.addAction(
        id='exportBib',
        name='Export Bibliography',
        action='string:${object_url}/bibliography_exportForm',
        permission='View',
        category='document_actions',
        condition='python:portal.isBibliographyExportable(object)',
        visible=1,
        )
     
def removeActionIcons(self):

    ai = getToolByName(self, 'portal_actionicons')

    # the ActionIcon tool is pretty picky with already existing icons, and easily causes product install
    # to fail with a KeyError: 'Duplicate definition!'. 
    #
    # To avoid this, this function is called on install AND uninstall
    
    for category, id in [('controlpanel', 'BibFlexViewSetup'),]:
	try:
    	    ai.removeActionIcon(category,id)
	except KeyError:
    	    pass
    	    
 
def installBibFolderActions(self, out):
    types_tool = getToolByName(self, 'portal_types', None)
    for bft in BIBFOLDERLIKE_TYPES:
        try:
            t = getattr(types_tool, bft)
            t.addAction(id = 'flex_view_settings',
                        name='Flexible View Settings',
                        action='string:${object_url}/bibfolder_flex_view_settings_form',
                        condition='python: object.portal_membership.checkPermission("Modify portal content", object)',
                        permission='Modify Portal content',
                        category='object' )
    
            if bft == 'BibliographyFolder': # besonderheit hier: 'view' zeigt auf 'base_view', das muessen wir loswerden
                # hab nich wirklich rausgefunden wie man actions aendert, deshalb loeschen wir die view action und erstellen ne neue
                idx = 0
                for actions in t.listActions():
                    if actions.getCategory() == 'object' and actions.getId() == 'view':
                        t.deleteActions((idx,))
                        break
                    idx += 1
            
                t.addAction(id = 'view',
                            name='View',
                            action='string:${object_url}',
                            condition='',
                            permission='View',
                            category='object' )
                                            
                # wie viel muessen wirs hochbewegen?
                i = len(t.listActions()) - 1
                while i > idx:
                    t.moveUpActions((i,))
                    i -= 1
        except AttributeError:
            if bft == 'BibliographyFolder':
                raise "Can't find the BibliographyFolder type. Is CMFBibliographyAT installed?\n"
            else:
                out.write('Could not find %s type, skipping set up of actions for that type. Once you install a product providing this type, be sure to reinstall BibfolderFlexibleView for full functionality\n' % bft)
                pass    
                                                
def uninstallBibFolderActions(self):
# XXX view zuruecksetzen, aber nich so dringend
    types_tool = getToolByName(self, 'portal_types', None)
    
    for bft in BIBFOLDERLIKE_TYPES:
        try:
            t = getattr(types_tool, bft)
        
            idx = 0
            for actions in t.listActions():
                if actions.getCategory() == 'object' and (actions.getId() == 'flex_view_settings'): # or actions.getId() == 'view'):
                    t.deleteActions((idx,))
                    idx-=1
                idx += 1
            # folgendes koennte man zwecks wiederherstellung des status davor machen - aber wozu?     
            # types_tool.BibliographyFolder.addAction(id = 'view',
            #                                         name='View',
            #                                         action='string:${object_url}/base_view',
            #                                         condition='',
            #                                         permission='View',
            #                                         category='object' )
        except AttributeError:
            if bft == 'BibliographyFolder':
                raise "Can't find the BibliographyFolder type. Is CMFBibliographyAT installed?"
            else:
                pass
   
def resetBibFolderLayout(self):
    catalog_tool = getToolByName(self, 'portal_catalog')
    bibfolders = catalog_tool(portal_type=BIBFOLDERLIKE_TYPES)
    bibfolders = [x.getObject() for x in bibfolders]
    for b in bibfolders:
        if b.hasProperty('layout'): b.manage_delProperties(['layout'])
   
def install(self):
    out=StringIO()

    removeActionIcons(self)
    setupSkin(self, out)
    addCatalogMetadata(self, out)
    setupTool(self, out)
    installBibFolderActions(self, out)
    addPrefsPanel(self, out)
    updateBibFolderProperties(self, out)
    setupDisplayViews(self, out, DISPLAY_VIEWS)

    out.write('Installation completed.\n')
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    removeActionIcons(self)
    undoMyActions(self, out)
    removePrefsPanel(self)
    uninstallBibFolderActions(self)
    resetBibFolderLayout(self)
    removeDisplayView(self, out, DISPLAY_VIEWS)
    #removeBibFolderProperties(self, out)

    # remove external methods from old version
    portal=getToolByName(self,'portal_url').getPortalObject()
    
    for script in ('BibfolderFlexibleView', ):
        if hasattr(aq_base(portal), script):
            meth = getattr(aq_base(portal), script)
            if meth.meta_type=='External Method':
                out.write('Deleting External Method.\n')
                portal.manage_delObjects(ids=[script,])
                
    
    return out.getvalue()   
