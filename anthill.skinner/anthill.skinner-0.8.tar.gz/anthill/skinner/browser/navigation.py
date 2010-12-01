
from zope.interface import implements
from Acquisition import aq_inner, aq_parent
from zope.component import queryMultiAdapter, getMultiAdapter

from zope.contentprovider.interfaces import IContentProvider

from Products.Archetypes.utils import shasattr
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

import plone.app.layout.viewlets.common
import plone.app.portlets.portlets.navigation
from plone.app.layout.navigation.root import getNavigationRoot

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree

from anthill.tal.macrorenderer import MacroRenderer

from anthill.skinner.config import DEFAULT_ROOTFOLDER_IGNORES
from interfaces import INavigationBase, ICustomMenuParameters

import types
ListTypes = [types.ListType, types.TupleType]

def _folderishContextOf(ct):
    folder = aq_inner(ct)
    if not IFolderish.providedBy(folder):
        folder = aq_parent(folder)
    return folder

class Assignment(plone.app.portlets.portlets.navigation.Assignment):
    """ Language enabled assignment """

    def __init__(self, name, **kw):
        self.name = name
        self.__dict__.update(kw)

def _getNavRenderer(context, request, instance):
    data = Assignment('publicmenu',
                currentFolderOnly=False, includeTop=instance.includeTop,
                topLevel=instance.topLevel, bottomLevel=instance.bottomLevel,
                Language=instance.Language)

    navrender = plone.app.portlets.portlets.navigation.Renderer(
                        _folderishContextOf(context), 
                        request,
                        view=None, manager=None, 
                        data=data)

    return navrender

def _isGlobalCurrent(context, url):
    ctpath = context.absolute_url()
    return ctpath.startswith(url)

class NavigationBase(BrowserView):
    """ @see: INavigationBase """

    implements(INavigationBase)

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

    def _render_viewlet(self, factory):
        # shamelessly copied from collective.skinny
        viewlet = factory(self.context, self.request, None, None).__of__(self.context)
        viewlet.update()
        return viewlet.render()

    def renderPathBar(self):
        return self._render_viewlet(plone.app.layout.viewlets.common.PathBarViewlet)

    def renderNavigation(self):
        return self._render_viewlet(plone.app.layout.viewlets.common.GlobalSectionsViewlet)

    def renderBackToCMSLink(self):
        folderish = _folderishContextOf(self.context)
        return '<a href="%s/@@skinner/deactivatePreview" i18n:translate="">Back to Plone</a>' % folderish.absolute_url()

    def navigationRoot(self):
        nroot = self.context.unrestrictedTraverse(getNavigationRoot(_folderishContextOf(self.context)))
        return nroot

    def hereIsRoot(self, template_id, excludes=DEFAULT_ROOTFOLDER_IGNORES, excludes_id=[]):

        # we need to check if we are looking at the default
        # page of the root folder
        _folder = _folderishContextOf(self.context)
        navroot_path = getNavigationRoot(_folder)
        default_root_path = getattr(self.context.unrestrictedTraverse(navroot_path), 'default_page', None)
        if default_root_path is not None and default_root_path == self.context.getId():
            ctid = 'IGNORE'
        else: ctid = self.context.getId()

        # add another switch to make sure that we can influence rootpath
        if self.request.get('showpage', None) is not None:
            return False

        if template_id not in excludes \
                and ctid not in excludes_id \
                and navroot_path == '/'.join(_folder.getPhysicalPath()):
            return True
        return False

    def isListType(self, t):
        """ Returns true if object is a list """

        return type(t) in ListTypes
   
    def filterOutObjectsWf(self, objects, state='published'):
        """ Returns all objects from the list that
        have the specified workflow state """

        wf = getToolByName(self.context, 'portal_workflow')
        if not self.isListType(objects):
            objects = [objects, ]

        if not self.isListType(state):
            state = [state, ]

        res = []
        for o in objects:
            try:
                if wf.getInfoFor(o, 'review_state') in state:
                    res.append(o)
            except: pass # do not include faulty objects

        return res
  
    def filterOutBrainsWf(self, brains, state):
        """ Returns all brains matching the given workflow state """

        if not self.isListType(brains):
            brains = [brains, ]

        if not self.isListType(state):
            state = [state, ]
            
        return [b for b in brains if b.review_state in state]

    def filterOutWf(self, listing, state):
        """ Returns all objects matching the given state.
        Objects can be brains or objects """

        if not self.isListType(listing):
            raise Exception, 'Argument must be a list. Is of type: %s' % type(listing)

        if len(listing) == 0:
            return []

        if hasattr(listing[0], 'getRID'):
            return self.filterOutBrainsWf(listing, state)
        else: return self.filterOutObjectsWf(listing, state)

    def folderObjects(self, folderpath, 
                     types, states=['published', ], 
                     full_objects=False, sort=False, reverse=False,
                     sort_on_field=None, sort_on_method=None,
                     aquire=False, language='all'):
        """ Returns all objects (as brains) belonging to the given
        folder by their portal_types and respecting the
        given workflow states. A * as state returns all states. """

        # make it possible to pass objects
        if shasattr(folderpath, 'getPhysicalPath'):
            folderpath = folderpath.getPhysicalPath()

        if self.isListType(folderpath):
            folderpath = '/'.join(folderpath)

        sort_on = 'getObjPositionInParent'
        if sort is True:
            sort_on = 'created'
       
        folder = self.context.restrictedTraverse(folderpath)
        filtered = folder.getFolderContents(
                contentFilter={'portal_type':types, 
                               'sort_on':sort_on, 
                               'Language' : language}, 
                full_objects=full_objects)

        if states is not '*':
            filtered = self.filterOutWf(list(filtered), states)
        
        # check if we have custom sort method
        if sort and sort_on_method:
            filtered.sort(lambda x,y: cmp(getattr(x, sort_on_method)(), 
                                          getattr(y, sort_on_method)()))
        
        if sort and sort_on_field:
            filtered.sort(lambda x,y: cmp(getattr(x, sort_on_field), 
                                          getattr(y, sort_on_field)))
      
        if reverse is True:
            filtered.reverse()

        if aquire and not filtered:
            if folderpath != self.context.portal_url.getPortalPath():
                parent = '/'.join(folderpath.split('/')[:-1])
                return self.folderObjects(parent, types, states, full_objects, sort, reverse,
                                                        sort_on_field, sort_on_method, aquire)
      
        return filtered
 
    def cutUpText(self, cutat, text, maxelongation=10, showellipsis=False):
        """ Function to cut up a long text.
        @cutat Position where to cut text
        @maxelongation If the cut position is in the
                       middle of a word then this param
                       determines how much characters
                       are included in resumee before cutting"""
        
        result = []
        counter = 0
        counter2 = 0

        whites = [' ', '\n', '\t', ',', '.']

        for char in text:
            counter += 1
            
            # ok - we have found the place where to cut
            if int(counter) == int(cutat):
                for cc in text[int(counter)-1:]:
                    counter2 += 1
                    
                    # white space?
                    if cc in whites: break
                    
                    # elongate text. that means that we don't
                    # cut words that have a length of <= max_elongation
                    if int(counter2) != int(maxelongation): 
                        result.append(cc)
                    else: break
                
                # stop right here
                break
            
            result.append(char)

        ellipsis = ''
        if (showellipsis != False) and (len(result) < len(text)):
            ellipsis = '...'

        return '%s%s' % (''.join(result), ellipsis)

    def objectTranslation(self, object, language=None):
        if shasattr(object, 'getURL'):
            object = object.getObject()

        lang = language
        if language == None:
            lang = object.portal_languages.getPreferredLanguage()

        translations = {} # lang:[object, wfstate]
        if object.isTranslatable():
            translations = object.getTranslations()
            available = translations.has_key(lang)
            if available:
                return translations.get(lang)[0]

            return object.getCanonical()

        # for non-translatable objects we return
        # the current one
        return object

    def menuIsActive(self, topLevel, bottomLevel):
        # algorithm is as follows:
        # - get the plone root path
        # - get the context path (folderish)
        # - check if current level of path == topLevel - 1 and < bottomLevel 
        # - check if there are any items displayable

        purl = getToolByName(self.context, 'portal_url')
        portal = aq_inner(purl.getPortalObject())

        # shortcuts
        if topLevel <= 0:
            return True

        # submenu of portal should always be active
        _fd = _folderishContextOf(self.context)
        if _fd is portal:
            return False

        portalpath = aq_inner(portal).getPhysicalPath()
        currentpath = _fd.getPhysicalPath()
        level = len(currentpath[len(portalpath):])

        levelok = (level >= (topLevel) and level <= bottomLevel)

        # it is a bit tricky to determine if there are items to be displayed
        # because we can't rely on a simple getFolderContents or such. Instead
        # we need to load the navtree engine and then check if there are any items
        # provided. This is a bit slow but there is no other way. We use the data
        # provided by PublicMenu here.
        cnav = queryMultiAdapter( (self.context, self.request, self), 
                                    name = u'anthill.skinner.PublicMenu')
        cnav.update()
        navok = len(cnav.data['children']) > 0

        return levelok and navok

class CustomNavigation(object):
    """ Custom navigation that relies on standard plone engine but simplifies life a bit
        by using templates diectly accessible by the user. """

    implements(ICustomMenuParameters, IContentProvider)

    enclosing_tag = None
    includeTop = True
    topLevel = 1
    bottomLevel = 65536
    showItemsInState = 'visible,published'
    Language = 'all'

    def __init__(self, context, request, view):
        self.context = aq_inner(context)

        # make sure we have a folder
        self.context = aq_inner(_folderishContextOf(self.context))

        self.request = request
        self.__parent__ = view

    def _getStates(self):
        return [t.strip() for t in self.showItemsInState.split(',')]

    def update(self):
        # we use Renderer directly here (querying multi adapter would be too
        # complicated for a portlet) in order to mimic the navtree portlet
        # as much as possible

        self.navrenderer = _getNavRenderer(self.context, self.request, self)

        # make sure to clear the navrenderer cache - for public view
        # this does not make sense - also we're having a singleton here
        from plone.memoize import instance
        instance.Memojito().clear(self.navrenderer)

        queryBuilder = getMultiAdapter((self.context, self.navrenderer.data), INavigationQueryBuilder)
        queryBuilder.query['Language'] = self.Language # make sure that language's included

        strategy = getMultiAdapter((self.context, self.navrenderer.data), INavtreeStrategy)
        self.data = buildFolderTree(self.context, obj=self.context, query=queryBuilder(), strategy=strategy)
        self.navroot = self.navrenderer.getNavRoot()

    def _computeMacroName(self, level, template):
        # we compute the macro name to be used. This is needed
        # because macro levels can be 'acquired'. If there is for
        # example no macro for level n we search for a def for n-1

        if level == 0:
            try:
                template.macros['level_0']
                return 'level_0'
            except:
                raise Exception, 'You must define a level 0!'

        levels = range(level); levels.reverse();
        for n in [f+1 for f in levels]:
            try:
                name = 'level_%s' % int(n)
                template.macros[name]
                return name
            except KeyError:
                continue

        raise Exception, 'You seem to have forgotten to define macro levels! Level: %s, Range: %s' % (level, range(level))

    def _recurse(self, template, level, node, topLevel):
        output = u''
        if level <= 0 or level <= self.bottomLevel:
            children = node.get('children', [])
            for child in children:

                # make sure we take review state into account
                if child['review_state'] not in self._getStates():
                    continue

                data = {'item' : child,
                        'isCurrent' : child['currentItem'],
                        'isGlobalCurrent' : _isGlobalCurrent(self.context, child['getURL'])}

                renderer = MacroRenderer(template, 
                                         self._computeMacroName(topLevel, template),
                                         context=self.context)
                output += renderer(data=data)

                if len(child['children']) > 0 and child['show_children']:
                    output += self._recurse(template, level+1, child, topLevel+1)

        return output

    def render(self):

        # load template (residing in portal_skins to ease customization)
        navtemplate = self.context.unrestrictedTraverse('publicmenu_levels')

        struct = {}
        for name in ['include_top', 'root_item_class', 'root_is_portal', 'navigation_root']:
            struct[name] = getattr(self.navrenderer, name)
       
        defout = u'%s'; output = u''
        if self.enclosing_tag != None:
            defout = '<%(tag)s>%%s<%(tag)s>' % {'tag' : self.enclosing_tag} 

        # render root item first and then children
        if self.includeTop is True:
            output += MacroRenderer(navtemplate, 'rootitem', context=self.context)(data=struct)

        output += self._recurse(navtemplate, level=int(self.topLevel), 
                                node=self.data, topLevel=self.topLevel)

        return defout % output

