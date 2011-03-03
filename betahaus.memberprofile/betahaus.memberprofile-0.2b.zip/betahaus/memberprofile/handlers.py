from Products.Archetypes.utils import shasattr
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName


def memberarea_added(context, event):
    """ Currently only active through a Plone4 event subscriber.
        - this adds the posibility of subscribing to Archetypes events
        - it also removes the creation-flag, so it doesn't look like you're creating something new
          when you edit the first time
    """
    if shasattr(context, '_at_creation_flag'):
        at_cf = getattr(context, '_at_creation_flag', False)
        if at_cf:
            context.unmarkCreationFlag()
            #Make sure rename after creation stuff is touched before notifying
            notify(ObjectInitializedEvent(context))


def sync_name(context, event):
    """ Sync first and last name with fullname.
        Some parts of Plone access the member property fullname, so it's good to keep it updated.
    """
    fullname = "%s %s" % (context.getFirstname(), context.getLastname())
    fullname = fullname.strip()
    context.getField('fullname').set(context, fullname)
    