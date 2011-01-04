from Products.Five import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName


class smart_keyword_edit_form_view(BrowserView):
    """
        Class for supporting the public view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        form = self.request.form

        # Get form data
        global_add = form.get('global_add', [])
        global_remove = form.get('global_remove', [])
        items = form.get('items', None)
        b_start = form.get('b_start', 0)
        b_size = form.get('b_size', self.b_size)

        # Cook tags
        global_add = self.cook(global_add)
        global_remove = self.cook(global_remove)

        if items:

            # Convert items into dictonnary
            items = dict([ (item["uid"], item) for item in items ])

            # Now proceed
            for item in self.context.queryCatalog():
                uid = item.UID
                values = items.get(uid, {})
                add = values.get("add", "")
                add = self.cook(add, False)
                delete = values.get("delete", [])
                self.modifyKeywords(uid, add + global_add, delete + global_remove)

    def cook(self, what, joinfirst = True):
        if joinfirst:
            what = self.separator.join(what)
        what = [ kw.strip() for kw in what.split(self.separator) ]
        what = [ kw for kw in what if kw ]
        return what

    def modifyKeywords(self, uid, add = [], delete = []):
        """
        Modify keywords of object
        """
        # Shortcut out of dummy calls
        if not add and not delete:
            return
        
        # Get object from catalog
        catalog = getToolByName(self, "portal_catalog")
        brains = catalog(UID = uid)
        if len(brains) != 1:
            # Oh, oh, what ?
            return
        brain = brains[0]

        # Compute lists of keywords
        old = tuple(brain.Subject)
        delete = set(delete)
        new = [ kw for kw in old if not kw in delete ]
        existing = set(new)
        for kw in add:
            if not kw in existing:
                new.append(kw)
        new = tuple(new)

        # If anything change, write it
        if new != old:
            obj = brain.getObject()
            obj.setSubject(new)
            obj.reindexObject()

    def getAllKeywords(self):
        """
        Return sorted list of tags
        """
        catalog = getToolByName(self, "portal_catalog")
        keywords = list(catalog.uniqueValuesFor('Subject'))
        keywords.sort()
        return keywords

    @property
    def separator(self):
        registry = getUtility(IRegistry)
        return registry['collective.smartkeywordmanager.separator']
    
    @property
    def b_size(self):
        registry = getUtility(IRegistry)
        return registry['collective.smartkeywordmanager.b_size']
