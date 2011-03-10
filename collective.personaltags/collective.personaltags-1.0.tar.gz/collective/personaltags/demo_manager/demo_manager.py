"""
    The source of the tags

    Ultimately these will be out in alchemy.

    This demo just stores the tags locally for all users

    Thanks to Martin for pointing out that I cannot lookup the
    user in a view __init__ method.

"""
from persistent.dict import PersistentDict as dict

from zope.interface import Interface
from zope.component import getUtility
from zope.app.component.hooks import getSite

from five import grok
from plone.dexterity.utils import createContent


from Products.CMFCore.utils import getToolByName 
from plone.registry.interfaces import IRegistry

from ..interfaces import ITagManager, IPersonalTagsSettings

STORAGE_NAME='personaltags'


class TagManager(grok.MultiAdapter):
    grok.adapts(Interface)
    grok.implements(ITagManager)
    grok.name(u'demo')

    defaultViewName= u'@@personaltags_listtags'

    _data = None
    contextid = None
    _principalid = None

    def __init__(self, context):
        self.context = context
        try:
            self.contextid = context.UID()
        except:
            pass
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IPersonalTagsSettings)


    @property
    def principalid(self):
        """Cannot do this in the __init__ method"""
        if self._principalid == None:
            mt =  getToolByName(self.context, 'portal_membership')
            if not mt.isAnonymousUser():
                try:
                    member = mt.getAuthenticatedMember()
                    self._principalid = member.getUserName()
                except:
                    pass

        return self._principalid

    @property
    def data(self):
        site = getSite()
        if STORAGE_NAME in site:
            storage = site[STORAGE_NAME]
        else:
            container = createContent('collective.personaltags.demo_storage', title='Personal Tags Demo Storage')
            storage = site[STORAGE_NAME] = container
            storage.data = dict()

        if self.principalid is not None:
            if self.principalid not in storage.data:
                storage.data[self.principalid] = dict({
                    'allTags': dict(),
                    'contexttags': dict(),
                    'hiddenTags': dict()
                })
            self._data = storage.data[self.principalid] 
        else:
            self._data = dict({
                'allTags': dict(),
                'contexttags': dict(),
                'hiddenTags': dict()
            })
        return self._data

    def getTagsForContext(self, include_hidden=False):
        """Return the tags for the context"""
        contexttags = self.data['contexttags']
        if include_hidden:
            hiddenTags = []
        else:
            hiddenTags = self.data['hiddenTags']
        if self.contextid in contexttags:
            return sorted([tag for tag in contexttags[self.contextid] if tag not in hiddenTags])
        return []

    def getAllTags(self, include_hidden=False):
        """Return the list of available tags"""
        if self.principalid is None:
            return []
        allTags = self.data['allTags']
        if include_hidden:
            hiddenTags = []
        else:
            hiddenTags = self.data['hiddenTags']

        # Include any system wide tag names
        rv = allTags.keys()
        system_tags = self.settings.system_tags.split(',')
        for st in system_tags:
            if st not in allTags:
                rv.append(st)
        return [tag.encode('utf8') for tag in rv if tag not in hiddenTags]

    def addTag(self, tag):
        if self.principalid is None or self.contextid is None:
            return
        contexttags = self.data['contexttags']
        allTags = self.data['allTags']
        tag = tag.lower()
        if self.contextid in contexttags:
            if tag in contexttags[self.contextid]:
                return
            contexttags[self.contextid].append(tag)
        else:
            contexttags[self.contextid] = [tag]
        if tag in allTags:
            allTags[tag] += 1
        else:
            allTags[tag] = 1

    def deleteTag(self, tag):
        if self.principalid is None or self.contextid is None:
            return
        contexttags = self.data['contexttags']
        allTags = self.data['allTags']
        tag = tag.lower()
        if self.contextid in contexttags and tag in contexttags[self.contextid]:
            contexttags[self.contextid].remove(tag)
        if tag in allTags:
            allTags[tag] -= 1
            # TODO: If content item deleted, you can end up with a hanging tag
            if allTags[tag] == 0:
                del allTags[tag]

    def getTagsAndCounts(self, include_hidden=False):
        """Return a list of tags and counts - this is the summary information.
        """
        if self.principalid is None:
            return []
        allTags = self.data['allTags']
        if include_hidden:
            hiddenTags = []
        else:
            hiddenTags = self.data['hiddenTags']
        return [(t, c) for (c, t) in sorted([(count, tag) for tag, count in allTags.items() if tag not in hiddenTags], key=lambda rec: (rec[0] * -1, rec[1]))]

    def editorAvailable(self):
        """
            Editor is available for non-anonymous users.
            If portal_type restrictions are configured, honour them
        
        """
        if self.principalid == None or self.contextid == None:
            return False
        if not self.settings.portal_types:
            return True
        return self.context.portal_type in self.settings.portal_types

    def portletAvailable(self):
        """Portlet is not available for anonymous users and is not displayed
        if you have no tags"""
        if self.principalid is None:
            return False

        tags_for_current_user = self.getTagsAndCounts()
        if len(tags_for_current_user) == 0:
            return False
        return True

    def getItemsForTag(self, tag):
        """
            Return the items tagged with the named tag
            The result is a catalog brains object
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        UIDS=[]
        if self.principalid is not None:
            for context, tags in self.data['contexttags'].items():
                if tag in tags:
                    UIDS.append(context)

        if UIDS:
            return catalog.searchResults(UID=UIDS)
        else:
            return []

    def getTagsAndStatus(self):
        """
            Return a list of dict with
            tag - name
            count - usage count
            system - true of false for system tag
            hidden - true or false for hidden
        """
        rv = []
        hiddenTags = self.data['hiddenTags']
        allTags = self.data['allTags']
        system_tags = self.settings.system_tags.split(',')
        for tag in system_tags:
            rec = {
                    'tag': tag,
                    'system': True,
                    'hidden': tag in hiddenTags,
                    'count': 0
                    }
            if tag in allTags:
                rec['count'] = allTags[tag]
            rv.append(rec)
        for tag in [t for t in allTags.keys() if t not in system_tags]:
            rec = {
                    'tag': tag,
                    'system': False,
                    'hidden': tag in hiddenTags,
                    'count':  allTags[tag]
                    }
            rv.append(rec)

        return rv


    def confShow(self, tag):
        """Configure the named tag so that it is shown"""
        hiddenTags = self.data['hiddenTags']
        tag = tag.lower()
        if tag in hiddenTags:
            del hiddenTags[tag]

    def confHide(self, tag):
        """Configure the named tag so that it is hidden"""
        hiddenTags = self.data['hiddenTags']
        tag = tag.lower()
        if tag not in hiddenTags:
            hiddenTags[tag] = 1

    def confDelete(self, tag):
        """Delete the named tag alltogether"""
        tag = tag.lower()
        hiddenTags = self.data['hiddenTags']
        if tag in hiddenTags:
            del hiddenTags[tag]
        allTags = self.data['allTags']
        if tag in allTags:
            del allTags[tag]
        contexttags = self.data['contexttags']
        for contextid in contexttags.keys():
            if tag in contexttags[contextid]:
                contexttags[contextid].remove(tag)
                if len(contexttags[contextid]) == 0:
                    del contexttags[contextid]

