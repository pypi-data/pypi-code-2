import re

from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url


class Page(Resource):
    def __repr__(self):
        return "<Page: %s>" % self.name
    
    def delete(self):
        """
        Delete this page.
        """
        self.manager.delete(self)
    
    def get_html(self):
        """
        Get the HTML of the page content.
        
        :rtype: string of HTML
        """
        return self.manager.get_html(self)
    
    def get_wikitext(self):
        """
        Get the WikiText of the page content.
        
        :rtype: string of WikiText
        """
        return self.manager.get_wikitext(self)
    
    def get_id(self):
        """
        Get the unique ID of the page. Returns the page_id attribute, if present,
        otherwise it will return a slug of the page name.
        
        :rtype: string
        """
        if hasattr(self, "page_id"):
            return self.page_id
        return self.name_to_id()
    
    def name_to_id(self):
        """
        Get a slug of the page name.
        
        :rtype: string
        """
        id = self.name or ''
        id, num = re.compile("[^\w0-9_-]+", re.U).subn('_', id)
        id, num = re.compile("_+").subn('_', id)
        id = re.compile("^_(?=.)").sub('', id)
        id = re.compile("(?<=.)_$").sub('', id)
        id = re.compile("^0$").sub('_', id)
        return id.lower()


class PageManager(Manager):
    """
    Manage :class:`Page` resources.
    """
    resource_class = Page
    
    def list(self, ws):
        """
        Get a list of all pages.
        
        :param ws_name: The :class:`Workspace` (or name of WS) to query
        :rtype: list of :class:`Page`.
        """
        url = make_data_url("pages", arguments_dict={"ws_name" : get_id(ws)})
        return self._list(url)
    
    def get(self, page, ws=None):
        """
        Get a specific page.
        
        :param page: The :class:`Page` to get
        :param ws: The :class:`Workspace` (or name of WS) the page belongs to.
        :rtype: :class:`Page`.
        """
        ws_name = None
        if isinstance(page, Page):
            ws_name = page.workspace_name
        else:
            ws_name = get_id(ws)
        
        url = make_data_url("page",
            arguments_dict={"ws_name" : ws_name, "page_name" : get_id(page)})
        return self._get(url)
    
    def get_html(self, page, ws=None):
        """
        Get the HTML representation of a specific page.
        
        :param page: The :class:`Page` to get
        :param ws: The :class:`Workspace` (or name of WS) the page belongs to.
        :rtype: :class:`Page`.
        """
        ws_name = None
        if isinstance(page, Page):
            ws_name = page.workspace_name
        else:
            ws_name = get_id(ws)
        
        url = make_data_url("page", arguments_dict={"ws_name" : ws_name, "page_name" : get_id(page)})
        headers = {'Accept' : 'text/html'}
        resp, body = self.api.client.get(url, headers=headers)
        return body
    
    def get_wikitext(self, page, ws=None):
        """
        Get the WikiText representation of a specific page.
        
        :param page: The :class:`Page` (or ID of Page) to get
        :param ws: The :class:`Workspace` (or name of WS) the page belongs to.
        :rtype: string of WikiText.
        """
        ws_name = None
        if isinstance(page, Page):
            ws_name = page.workspace_name
        else:
            ws_name = get_id(ws)
        
        url = make_data_url("page", arguments_dict={"ws_name" : ws_name, "page_name" : get_id(page)})
        headers = {'Accept' : 'text/x.socialtext-wiki'}
        resp, body = self.api.client.get(url, headers=headers)
        return body
    
    def create(self, name, ws, body, tags=[], edit_summary=None, signal_edit_summary=False):
        """
        Create a page in Socialtext.
        
        :param ws: The :class:`Workspace` (or name of WS) to create the page in.
        :param name: Something to call the page.
        :param body: The WikiText content of the page.
        :param tags: A list of strings to add as tags on the page.
        :param edit_summary: A message summarizing the transaction.
        :param signal_edit_summary: If True, then send a signal whose body
                                    is the edit summary. This signal is targeted
                                    at the account to which the workspace belongs.
        
        :rtype: the new :class:`Page`
        """
        page = {"content" : body}
        if tags:
            page["tags"] = tags
        if edit_summary:
            page["edit_summary"] = edit_summary
        if signal_edit_summary:
            page["signal_edit_summary"] = 1
        url = make_data_url("page", arguments_dict={"ws_name" : get_id(ws), "page_name" : name })
        self._update(url, page)
        
        page = self.load({'workspace_name': get_id(ws), 'name': name})
        page.get()
        
        return page
    
    def delete(self, page, ws=None):
        """
        Delete a page in socialtext
        
        :param page: The :class:`Page` to get
        :param ws: The :class:`Workspace` (or name of WS) the page belongs to.
        """
        ws_name = None
        if isinstance(page, Page):
            ws_name = page.workspace_name
        else:
            ws_name = get_id(ws)
        
        url = make_data_url("page", arguments_dict={"ws_name": ws_name, "page_name": get_id(page)})
        self._delete(url)
