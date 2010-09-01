from StringIO import StringIO

try:
   from plone.app.upgrade import v40
   HAS_PLONE30 = True
   HAS_PLONE40 = True
except ImportError:
   HAS_PLONE40 = False
   try:
       from Products.CMFPlone.migrations import v3_0
   except ImportError:
       HAS_PLONE30 = False
   else:
       HAS_PLONE30 = True

def install_plone3_portlets(self):
    """Adds the discountable portlet to the root of the site
    so that it shows up on discountable items
    """
    if not HAS_PLONE30:
        return

    # Do the imports here, as we only need them here and this only
    # gets run on Plone 3.0.
    from zope.app.container.interfaces import INameChooser
    from zope.component import getUtility, getMultiAdapter
    from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
    from getpaid.discount.browser.portlets import portlets30

    # Get some definitions.
    portal = self.portal_url.getPortalObject()
    column = getUtility(IPortletManager, name="plone.rightcolumn", context=portal)
    manager = getMultiAdapter((portal, column), IPortletAssignmentMapping)
    portletnames = [v.title for v in manager.values()]
    chooser = INameChooser(manager)

    assignments = [
        portlets30.DiscountableAssignment(),
        portlets30.BuyXGetXfreeableAssignment(),
        ]

    for assignment in assignments:
        title = assignment.title
        if title not in portletnames:
            manager[chooser.chooseName(title, assignment)] = assignment

def setupVarious(context):
    """Import steps that are not handled by GS import/export handlers can be
    defined in the setupVarious() function.
    """
    if context.readDataFile('getpaid.discount-default.txt') is None:
        return

    site = context.getSite()

    logger = context.getLogger("getpaid.discount-default")
    out = StringIO()

    if HAS_PLONE30:
        print >> out, "Installing Discount Plone 3 Portlets"
        install_plone3_portlets(site)
    
    logger.info(out.getvalue())
    
    return "Setup various finished"

