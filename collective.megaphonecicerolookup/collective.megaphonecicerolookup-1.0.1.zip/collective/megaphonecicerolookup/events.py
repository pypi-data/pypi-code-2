from zope.component import adapter
from Products.Archetypes.interfaces import IObjectEditedEvent
from collective.megaphone.interfaces import IMegaphone
from collective.megaphone.recipients import get_recipient_settings

@adapter(IMegaphone, IObjectEditedEvent)
def update_required_fields(pfg, event):
    # if there are any Cicero lookup recipients, we need to make sure the address
    # fields used in the lookup are required.
    if len(get_recipient_settings(pfg, 'cicero_address_lookup')):
        for fname in ('street', 'city', 'state', 'zip'):
            field = getattr(pfg, fname, None)
            if field is not None:
                field.setRequired(True)
