
import zope.schema
from zope.interface import Interface, directlyProvides
from zope.contentprovider.interfaces import ITALNamespaceData

class ISkinHandler(Interface):
    """ Handler that provides functionality to switch between
        public view and plone default skin. """

    def activatePreview():
        """ Switches skin to public mode """

    def deactivatePreview():
        """ Switches skin back to default """

    def inPreview():
        """ Returns True if currently in preview mode """

    def inPublicView():
        """ Returns True if system is in public view. Will also return
            True if only in preview mode. """

    def activatePublicSkin():
        """ Activates public skin by setting appropriate layers """

    def mustDisplayPublicView():
        """ Returns True if public view has to be displayed """

class INavigationBase(Interface):
    """ Simple view providing methods to use path bar and section top
        viewlets (from plone). If you want completely customized navigation then
        use INavigationExtended implementation. """

    def renderNavigation():
        pass

    def renderPathBar():
        pass

    def renderBackToCMSLink():
        pass

    def menuIsActive(topLevel, bottomLevel):
        pass

    def hereIsRoot(templates_id, excludes=[]):
        pass

    def objectTranslation(obj, language=None):
        pass

    def cutUpText(cutat, text, maxelongation=10, showellipsis=False):
        pass

    def folderObjects(folderpath, types, states, full_objects=False):
        pass

    def isListType(t):
        pass

    def navigationRoot():
        pass

class ICustomMenuParameters(Interface):
    """ Holds available parameters for the custom menu content provider """

    enclosing_tag = zope.schema.Text(title=u'The enclosing tag for menu generation',
                                     default=None)

    topLevel = zope.schema.Int(title=u'The level of the items to start at - starts at 1',
                                default=1)

    bottomLevel = zope.schema.Int(title=u'The level of the items to stop at',
                                    default=65536)

    includeTop = zope.schema.Bool(title=u'Should we include top level folder',
                                     default=True)

    showItemsInState = zope.schema.Text(title=u'Workflow states of items to display',
                                    default=u'visible,published')

    Language = zope.schema.Text(title=u'Language for items',
                                    default=u'all')

# we need to mark this interface to make the implementing class accept params
directlyProvides(ICustomMenuParameters,
                 ITALNamespaceData)
