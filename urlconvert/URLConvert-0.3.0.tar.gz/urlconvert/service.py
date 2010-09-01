import warnings
import logging

from urlconvert import extract_url_parts
from bn import AttributeDict, absimport

log = logging.getLogger(__name__)

def urlService(make_ruleset):
    """
    To use this service effectievely outside a web environment you currently 
    have to specify the ``SERVER_NAME`` and ``SERVER_PORT`` explicitly in the
    ``environ`` dictionary.
    """
    internal_state={'ruleset': None}
    def urlService_constructor(service):
        name = service.name 
        def start(service):
            if internal_state['ruleset'] is None:
                internal_state['ruleset'] = make_ruleset(service) 
            service[name] = AttributeDict()
    
            def url_for(*k, **p):
                warnings.warn("service.url.url_for() has been replaced by service.url.generate()", DeprecationWarning)
                if k:
                    raise Exception(
                        'You cannot have keyword arguments when using URLConvert'
                    )
                url_parts = extract_url_parts(service)
                result = internal_state['ruleset'].generate_url(p, url_parts)
                return result
    
            def match(url=None):
                 if isinstance(url, unicode):
                     # It is a URL as a string
                     raise NotImplementedError
                 elif isinstance(url, dict):
                     # Assume it is a url_parts dict
                     url_parts = url
                 elif url is None:
                     try:
                         url_parts = extract_url_parts(service)
                     except Exception, e:
                         log.error('%s', e)
                         return None
                 else:
                     raise TypeError('The argument to match() should be a Unicode string or a dictionary of URL parts, not %r'%url)
                 conversion = internal_state['ruleset'].match(url_parts)
                 if not conversion.successful:
                     return None
                 return conversion.result
    
            def generate(vars, default_url_parts=None):
                 if default_url_parts is None:
                     default_url_parts = extract_url_parts(service)
                 return internal_state['ruleset'].generate_url(vars, default_url_parts)
    
            service[name]['url_for'] = url_for
            service[name]['generate'] = generate
            service[name]['match'] = match
            vars = match()
            service[name]['vars'] = vars and AttributeDict(vars) or AttributeDict()
        return AttributeDict(start=start)
    return urlService_constructor
