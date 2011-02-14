__version__ = "0.1.a1"

from socialtext.client import SocialtextClient
from socialtext.exceptions import (SocialtextException, BadRequest,
    Unauthorized, Forbidden, NotFound)
from socialtext.resources import PageManager, Page
from socialtext.resources import SignalManager, Signal
from socialtext.resources import UserManager, User
from socialtext.resources import WebhookManager, Webhook
from socialtext.resources import WorkspaceManager, Workspace

class Socialtext(object):
    """
    Top-level object to access the Socialtext API.
    
    Create an instance with your credentials::
        
        >>> st = Socialtext(server_url, username, password)
        
    Then call methods on its managers::
    
        >>> st.signals.list()
        ...
        >>> st.webhooks.list()
        ...
        
    &c.
    """
    
    def __init__(self, server_url, username, password):
        self.pages = PageManager(self)
        self.client = SocialtextClient(server_url, username, password)
        self.signals = SignalManager(self)
        self.users = UserManager(self)
        self.webhooks = WebhookManager(self)
        self.workspaces = WorkspaceManager(self)
    