__version__ = "0.1.a2"

from socialtext.client import SocialtextClient
from socialtext.exceptions import (SocialtextException, BadRequest,
    Unauthorized, Forbidden, NotFound, Conflict, RequestEntityTooLarge)
from socialtext.resources import PageManager, Page
from socialtext.resources import (ApplianceConfiguration,
    ApplianceConfigurationManager)
from socialtext.resources import SignalManager, Signal
from socialtext.resources import UploadManager
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
    
    """
    
    def __init__(self, server_url, username, password):
        self.pages = PageManager(self)
        self.client = SocialtextClient(server_url, username, password)
        self.config = ApplianceConfigurationManager(self)
        self.signals = SignalManager(self)
        self.uploads = UploadManager(self)
        self.users = UserManager(self)
        self.webhooks = WebhookManager(self)
        self.workspaces = WorkspaceManager(self)

    def impersonate(self, username):
        """
        Make API calls on behalf of the given user. Only calls to URIs
        in the /data/accounts or /data/workspaces routes are permitted.
        The API user must have impersonator permissions in the target
        :class:`Account` or target :class:`Workspace`.

        Example::

            # set the impersonation
            st.impersonate("joeuser")

            # clear the impersonation
            st.impersonate("")

        :param username: The username of the :class:`User` to impersonate.
        """
        self.client.impersonate(username)
