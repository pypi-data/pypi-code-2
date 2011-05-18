from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.cache import patch_vary_headers


class LocaleMiddleware(object):
    
    def process_request(self, request):
        """
        If the `request.path` starts with a (valid) language-code prefix, this
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
        Set the Content-Language header. If `response.status_code` is 404, and
        no language-code prefix is found, return a `HttpResponseRedirect` to the
        language-code prefixed `request.path`.
        """
        patch_vary_headers(response, ('Accept-Language',))
        language_code = translation.get_language()
        translation.deactivate()
        
        if 'Content-Language' not in response:
            response['Content-Language'] = language_code
        
        if response.status_code == 404 and not self._language_code_from_path(request.path):
            return HttpResponseRedirect('/%s%s' % (language_code, request.get_full_path()))
        else:
            return response
    
    def _language_code_from_path(self, path):
        """
        Return the language-code found in the requested path. For example
        `/en/my/path/` will return `en`. Return `None` if no language-code
        could be found.
        """
        language_code = None
        path_parts = path.split('/')
        if len(path_parts) > 2:
            possible_language_code = path_parts[1]
            for language in settings.LANGUAGES:
                if language[0] == possible_language_code:
                    language_code = possible_language_code
        return language_code
