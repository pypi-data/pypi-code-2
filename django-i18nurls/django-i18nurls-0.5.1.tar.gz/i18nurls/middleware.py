import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation


language_code_prefix_regex = re.compile(r'^/([\w-]+)/')

class LocaleMiddleware(object):
    
    def process_request(self, request):
        """
        If `request.path` starts with a (valid) language-code prefix, this
        language-code will be activated. Else `get_language_from_request` is
        used as a fallback.
        """
        language_code = self._language_code_from_path(request.path)
        
        if not language_code:
            language_code = translation.get_language_from_request(request)
        
        translation.activate(language_code)
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        """
        Sets the Content-Language header. If `response.status_code` is 404, and
        no language-code prefix is found, returns a `HttpResponseRedirect` to the
        language-code prefixed `request.path`.
        """
        language_code = translation.get_language()
        translation.deactivate()
        
        if 'Content-Language' not in response:
            response['Content-Language'] = language_code
        
        if response.status_code == 404 and not self._language_code_from_path(request.path):
            return HttpResponseRedirect('/%s%s' % (language_code, request.get_full_path()))
        else:
            return response
    
    def _language_code_from_path(self, path):
        regex_match = language_code_prefix_regex.match(path)
        if regex_match:
            if regex_match.group(1) in dict(settings.LANGUAGES):
                return regex_match.group(1)
        return None
