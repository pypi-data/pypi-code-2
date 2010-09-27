from zope.interface import noLongerProvides
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from themetweaker.themeswitcher.traverser import THEMESWITCHER_ANNO
from themetweaker.themeswitcher.interfaces import IThemeSwitcher

def uninstallCleanup(context):
    """Clean up interfaces and annotations left behind
    """
    if context.readDataFile('themetweaker.themeswitcher_uninstall.txt') is None:
        return
    portal = context.getSite()
    pc = getToolByName(portal, 'portal_catalog')
    res = pc(object_provides=IThemeSwitcher.__identifier__)
    for brain in res:
        obj = brain.getObject()
        # remove the annotations
        annotation = IAnnotations(obj)
        if THEMESWITCHER_ANNO in annotation:
            del annotation[THEMESWITCHER_ANNO]
        # remove the interface from the obj
        noLongerProvides(obj, IThemeSwitcher)
