from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url


class Workspace(Resource):
    def __repr__(self):
        return "<Workspace: %s>" % self.name

    def delete(self):
        """
        Delete the current workspace.
        """
        self.manager.delete(self)
    
    def get_id(self):
        """
        Return the ID of the workspace. Defaults to the workspace name
        if present, otherwise returns the primary key (ID).

        :rtype: string
        """
        assert hasattr(self, 'name') or hasattr(self, 'id'), "The workspace does not have a 'name' or 'id' attribute"
        return self.name if self.name else self.id


class WorkspaceManager(Manager):
    """
    Manage :class:`Workspace` resources.
    """
    resource_class = Workspace
    
    def list(self):
        """
        Get a list of all workspaces.
        
        :rtype: list of :class:`Workspace`.
        """
        url = make_data_url("workspaces")
        return self._list(url)
        
    def get(self, ws):
        """
        Get a specific workspace.
        
        :param ws: The :class:`Workspace` (or name of the workspace) to get.
        :rtype: :class:`Workspace`.
        """
        url = make_data_url("workspace", arguments_dict={"ws_name": get_id(ws)})
        return self._get(url)
        
    def create(self):
        raise NotImplementedError
        
    def delete(self, ws):
        """
        Delete a workspace in socialtext
        
        :param ws: The :class:`Workspace` (or name of the Workspace) to delete.
        """
        url = make_data_url("workspace", arguments_dict={"ws_name": get_id(ws)})
        self._delete(url)
