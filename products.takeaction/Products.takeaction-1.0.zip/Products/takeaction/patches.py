from Acquisition import aq_inner
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName

@memoize
def patchedContextStateActions(self, category=None, max=-1):
    # Unfortunately, the portal_actions ActionProvider functionality has been
    # completely bypassed in plone.app.layout >= 2.0a1
    # Reinstate it with a wrapper
    actions = self._old_actions(category, max)
    if category is None:
        # In this case portal_takeaction was involved anyway
        return actions

    context = aq_inner(self.context)
    atool = getToolByName(context, 'portal_actions')
    if 'portal_takeaction' not in atool.listActionProviders():
        # Not active
        return actions

    takeaction = getToolByName(context, 'portal_takeaction')
    actions.extend(takeaction.listActionInfos(
        object=context, categories=(category,), max=max))

    return actions
