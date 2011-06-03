def __init__():

    global SideBySideView, NoSideBySideView

    from AccessControl import ClassSecurityInfo
    from plone.app.iterate.interfaces import IWorkingCopy
    from plone.app.iterate.relation import WorkingCopyRelation
    from Products.Five.browser import BrowserView
    from Products.CMFCore import permissions

    class SideBySideView(BrowserView):
        """Provide some helper methods to be used inside the (form controller
        based) side-by-side editing view."""
        security = ClassSecurityInfo()

        security.declareProtected(permissions.View, 'getCanonical')
        def getCanonical(self):
            """Returns the canonical translation."""
            ret = self.context
            refs = ret.getTranslationReferences()
            if len(refs):
                ret = self._getReferenceObject(uid=refs[0].targetUID)
            return ret

        security.declareProtected(permissions.View, 'getBaselineCopy')
        def getBaselineCopy(self):
            """Return the original copy, or self.context if this is not a working copy."""
            if IWorkingCopy.providedBy(self.context):
                return self.context.getReferences(WorkingCopyRelation.relationship)[0]
            return self.context

        security.declareProtected(permissions.View, 'isEnabled')
        def isEnabled(self):
            """Should side-by-side tab be visible for this content?"""
            return self.context != self.getBaselineCopy()

    class NoSideBySideView(SideBySideView):
        def isEnabled(self): return False

__init__()
