import logging
import transaction
from types import UnicodeType

from Products.CMFCore.utils import getToolByName

from slc.cleanwordpastedtext import update_object_history
from slc.cleanwordpastedtext import get_unicode_text
from slc.cleanwordpastedtext import get_rich_text_fields
from slc.cleanwordpastedtext import clean_word_text

log = logging.getLogger('cleanWordPastedText')

def write(filename, msg): 
    f = open(filename, 'a+')
    f.write('%s' % msg.encode('ascii', 'replace'))
    f.close()
    return

def run(self):
    """ """
    ll = []
    portal_type = self.REQUEST.get('portal_type', 'Document')
    for o in query_objs(self, portal_type, 20):
        fs = get_rich_text_fields(o)
        if len(fs):
            for f in fs:
                old_text = get_unicode_text(f.getAccessor(o)())
                text = clean_word_text(old_text)
                assert type(text) == UnicodeType
                if old_text != text:
                    path = '/'.join(o.getPhysicalPath())
                    write('cleaned_objects.log', path+'\n')
                    write('cleaned_objects.log', text+'\n\n')
                    log.info(path)
                    ll.append(path)
                    f.getMutator(o)(text)
                    update_object_history(o)
                    
        if len(ll) and not len(ll)%1000:
            transaction.commit()
            log.info('transaction.commit(), %d' % len(ll))
    t = 'Cleaned up %d %s objects' % (len(ll), portal_type)
    write('cleaned_objects.log', t+'\n\n')
    log.info(t)

    if len(ll):
        return '%d objects affected' % len(ll)
    else:
        return '0 objects affected'

def query_objs(self, portal_type, limit=-1):
    catalog = getToolByName(self, 'portal_catalog')
    if limit > 0:
        return [o.getObject() for o in catalog(portal_type=portal_type)[:limit]]
    return [o.getObject() for o in catalog(portal_type=portal_type)]

