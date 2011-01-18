from command import Command

from ckanclient import CkanClient

class ApiCommand(Command):
    def __init__(self, usage=None):
        '''
        Base class for commands that use the API
        '''
        self.parser = Command.StandardParser(usage=usage)
        self.parser.add_option("-H", "--host",
                          dest="api_url",
                          help="API URL (e.g.: http://test.ckan.net/api)")
        self.parser.add_option("-k", "--key",
                          dest="api_key",
                          help="API Key (required)")
        self.parser.add_option("-u", "--username",
                          dest="username",
                          help="Username for HTTP Basic Authentication")
        self.parser.add_option("-p", "--password",
                          dest="password",
                          help="Password for HTTP Basic Authentication")
        if hasattr(self, 'add_options'):
            self.add_options()
        super(ApiCommand, self).__init__()

    def command(self):
        if not self.options.api_key:
            self.parser.error('Please specify an API Key')
        if not self.options.api_url:
            self.parser.error('Please specify an API URL')

        self.client = CkanClient(base_location=self.options.api_url,
                                 api_key=self.options.api_key,
                                 http_user=self.options.username,
                                 http_pass=self.options.password)

        # now do command
