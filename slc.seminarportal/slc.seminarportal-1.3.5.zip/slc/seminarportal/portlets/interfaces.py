from zope import schema
from zope.interface import Interface

from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone import PloneMessageFactory as _

class ISpeakerPortlet(IPortletDataProvider):
    """Interface for portlet to display seminar speakers
    """
    featured_speakers = schema.List(
                    title=u"Choose a speaker",
                    description= \
                            u'This field is not required if you choose to '
                            u'randomly display speakers or show only speakers '
                            u'from the current seminar.',
                    required=False,
                    value_type=schema.Choice(
                        vocabulary="slc.seminarportal.vocabularies.speakers")
                    )
                        
    count = schema.Int( 
                    title=u"How many speakers should be displayed?",
                    description= \
                            u"If you choose more speakers than should be "
                            u"displayed, the shown speakers will be chosen "
                            u"randomly from your specified list.",
                    required=True,
                    default=5
                    )
                         
    random = schema.Bool(
                    title=u'Option: Click here to display random speakers',
                    required=False,
                    default=True,
                    )

    local = schema.Bool(
                    title=u'Option: Click here to display only speakers '
                        u'from the current Seminar.',
                    description=u'This option will only take effect if the '
                        u'portlet is displayed inside a Seminar. Selecting '
                        u'this option takes precedence over the "random" '
                        u'selection above.',
                    required=False,
                    default=False,
                    )

    def get_speakers():
        """ """

class ISpeechesPortlet(IPortletDataProvider):
    """Interface for portlet to display seminar speeches 
    """
    count = schema.Int( 
                    title=u'How many speeches should be displayed?',
                    required=True,
                    default=5
                    )

    def get_speaker():
        """ """

class ISearchPortlet(Interface):
    """Interface for portlet to search inside seminars
    """

