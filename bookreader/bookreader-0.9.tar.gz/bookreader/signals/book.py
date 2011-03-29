from logging import getLogger
from urllib2 import URLError

from bookreader import harvesting



log = getLogger('bookreader.signals.book')

def load_metadata(sender, instance, **kwargs):
    try:
        if instance.published:
            harvesting.BookHarvester(instance).update_metadata()
    except URLError:
        log.debug('Unable to contact the repository')
    except:
        log.exception('Error harvesting book metadata')

def load_pages(sender, instance, created, **kwargs):
    if created:
        #harvesting.load_pages(instance)
        pass

def load_links(sender, instance, created, **kwargs):
    if created:
        #harvesting.load_links(instance)
        pass
