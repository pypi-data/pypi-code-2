from logging import getLogger
from urllib2 import URLError



log = getLogger('bookreader.signals.repository')

def lookup_name(sender, instance, **kwargs):
    try:
        instance.name = unicode(instance.connection().getName())
    except URLError:
        log.debug('Unable to contact the repository')
    except:
        log.exception('Unable to get the repository name automatically')
    
