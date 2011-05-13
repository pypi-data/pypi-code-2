from zope.interface import Interface


class IBuzzFolder(Interface):
    """A folder for Buzz items
    """


class IBuzz(Interface):
    """Buzz item
    """


class ICaseStudyFolder(Interface):
    """A folder for case studies
    """


class ICaseStudy(Interface):
    """Case study content
    """


class IProviderFolder(Interface):
    """A folder for providers
    """


class IProvider(Interface):
    """Provider content item
    """


class ISiteUsingPloneFolder(Interface):
    """A folder for Sites using Plone
    """


class ISiteUsingPlone(Interface):
    """Site using Plone content item
    """
