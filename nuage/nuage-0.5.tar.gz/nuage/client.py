import httplib2


class NuageClient(object):
    """
    Nuage API client
    """

    API_VERSION = 'v1'
    API_URL = 'http://nuagehq.com/api/%s' % API_VERSION,

    urls = dict(
        cli_version='%s/cli/version' % API_URL,
        )

    def __init__(self):
        self._http_client = httplib2.Http()

    def get(self, *args, **kwargs):
        self._http_client.request(*args, method="GET", **kwargs)

    def post(self, *args, **kwargs):
        self._http_client.request(*args, method="POST", **kwargs)

    def put(self, *args, **kwargs):
        self._http_client.request(*args, method="PUT", **kwargs)

    def delete(self, *args, **kwargs):
        self._http_client.request(*args, method="DELETE", **kwargs)

    def get_cli_version(self):
        #self.post(self.urls['cli_version'])
        return '0.5'
