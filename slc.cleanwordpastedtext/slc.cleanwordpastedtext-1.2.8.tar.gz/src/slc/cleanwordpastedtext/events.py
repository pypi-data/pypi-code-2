import logging

from types import UnicodeType

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from slc.cleanwordpastedtext.utils import clean_word_text
from slc.cleanwordpastedtext.utils import get_rich_text_fields
from slc.cleanwordpastedtext.utils import get_unicode_text
from slc.cleanwordpastedtext.utils import update_object_history

log = logging.getLogger('slc.cleanwordpastedtext/events.py')

def clean_word_pasted_text(event, *args):
    """ Event handler registered for object editing
    """
    obj = event.object

    if not hasattr(obj, 'Schema'):
        return
    field = obj.Schema().get('cleanWordPastedText')
    do_cleanup = field and field.get(obj) 
    if not do_cleanup:
        return 

    fs = get_rich_text_fields(obj)
    for f in fs:
        old_text = get_unicode_text(f.getAccessor(obj)())
        if old_text is None:
            return 

        text = clean_word_text(old_text)
        if  type(text) == UnicodeType and old_text != text:
            path = '/'.join(obj.getPhysicalPath())
            log.info('Cleaned the MS Word pasted text for %s' % path)
            f.getMutator(obj)(text)
            update_object_history(
                    obj, 
                    comment='Cleaned up HTML in the Rich-Text fields')

            putils = getToolByName(obj, 'plone_utils')
            putils.addPortalMessage(
                _("The HTML in the Rich-Text field(s) of this object has "
                "been cleaned up. This might result in lost formatting. "
                "You can disable automatic HTML cleanup by clicking on the "
                "'edit' tab and then checking the box in the 'settings' "
                "section."), 
                type="info")
                
