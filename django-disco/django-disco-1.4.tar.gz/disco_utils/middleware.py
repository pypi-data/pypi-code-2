class ReverseProxyMiddleware(object):
    """
    Adjust the script name of the request to account for different URL
    resulting from reverse proxying.
    """

    def process_request(self, request):
        script_name = request.META.get('HTTP_X_SCRIPT_NAME', None)
        if script_name is not None:
            request.META['SCRIPT_NAME'] = script_name
            path_info = request.path_info
            if path_info.startswith(script_name):
                path_info = path_info[len(script_name):]
                request.path_info = path_info

        scheme = request.META.get('HTTP_X_SCHEME', None)
        if scheme is not None:
            request.META['wsgi_url_scheme'] = scheme
