# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
import operator
from lxml import html
from piratebay.utils import open_url_with_request
from piratebay.parser import find_table, process_all_rows, find_number_of_pages, process_user_row
from piratebay import exceptions

search_page_url = "http://thepiratebay.org/s/?"
user_page_url = "http://thepiratebay.org/user/%s/%d/%d"

order = {
    'name': 1,
    'uploaded': 3,
    'size': 5,
    'uploader': 11,
    'seeders': 7,
    'leechers': 9
}

def search_main(term, category=0, page=0, order_by=order["seeders"], timeout=None):
    """Search the main piratebay website for the term 'term'.
    
    *Arguments*
        term = search with term.
        category = category from piratebay.categories.categories dict.
        page = the number of the search page to visit.(0 being default).
        order_by = the order of which piratebay should order it's results.(default being piratebay.page.order["seeders"])
    *Returns*
        a Page() object.
    """
    form_data = { "q": term, "category": category,
                "page": page, "orderby": order_by }
    url = open_url_with_request(search_page_url, form_data=form_data, timeout=timeout)
    doc = html.parse(url).getroot()
    return Page(doc, form_data=form_data)

def search_user(user, page=0, order_by=order["seeders"]):
    """Search the entries on a users page on piratebay.
    
    It is not an actual search, it basically just queries the users page
    to get all the releases from that user. Then order it by seeders as default,
    but can be changed with the order_by argument.
    """
    url = open_url_with_request(user_page_url % (user, page, order_by), timeout=timeout)
    doc = html.parse(url).getroot()
    return UserPage(doc)

class PageItem(object):
    def __init__(self, dct):
        self.data = dct
        
    def __getattr__(self, attr):
        if attr in self.data.keys():
            return self.data[attr]
        raise AttributeError("'PageItem' object has no attribute '%s'" % attr)
    
    def __str__(self):
        return """<PageItem
            name => %s
            torrent info url => %s
            torrent url => %s
            magnet url => %s
            user => %s
            seeders => %d
            leechers => %d
        >""" % (self.data['name'], self.data['torrent_info_url'],\
                self.data['torrent_url'], self.data['magnet_url'],\
                self.data['user'], self.data['seeders'], self.data['leechers'])

class BasePage(object):
    """Base class of all Page types."""

    def __init__(self, document, form_data=None):
        self.form_data = form_data
        self.document = document
        self.list_of_rows = None
        self.current_page = 0
        self.max_page = 0
        self._process_document()
    
    def search(self, key, value, comparator=None, order_by=None, reversed=True, limit=None):
        """Searched through each record in the dictionary, and yields the results(s).
        
        You can search for any 'value' in the dictionary with 'key', using
        operator.eq(==) by doing: page.search("user", "..."). Or you could use your
        own comparator method, as an example:
            >>> def compare_user(dict_value, your_search_term):
            ...     user = dict_value.encode("utf-8").split("/")
            ...     if len(user) >= 2:
            ...         user = user[-2]
            ...     if user == your_search_term:
            ...         return True
            ...     return False
            ...
            >>> from piratebay.page import search_main
            >>> page = search_main("some search term")
            >>> page.search("user", "some_user", comparator=compare_user, order_by="seeders")
        Would yield all result(s) and order them by seeders (LOCALLY), having the highest value first.
        
        *Arguments*
            key = Dict key to make the search on.
            value = The value to search for on that key.
            comparator = A predicate function to use for the search.
            order_by = How to order the results for the search.
            reveresed = If the order should be reversed.
        *Returns*
            A generator object having the results of the search.
        """
        if order_by is not None:
            self.list_of_rows = sorted(self.list_of_rows, key=operator.attrgetter(order_by), reverse=reversed)
        if comparator is None:
            comparator = operator.eq
        for index, row in enumerate(self.list_of_rows):
            if limit is not None:
                if index < limit and comparator(getattr(row, key), value):
                        yield row
                else:
                    break
            else:
                if comparator(getattr(row, key), value):
                    yield row
    
    def all(self, order_by=None, reversed=True, limit=None):
        """A generator that yields all torrents in turn."""
        if order_by is not None:
            self.list_of_rows = sorted(self.list_of_rows, key=operator.attrgetter(order_by), reverse=reversed)
        for index, row in enumerate(self.list_of_rows):
            if limit is not None:
                if index < limit:
                    yield row
                else:
                    break
            else:
                yield row

    def get_current_page(self):
        """Return the current page you're visiting."""
        return self.current_page
    
    def get_number_of_pages(self):
        """Return maximum number of pages available for your search."""
        return self.max_page

class Page(BasePage):
    """The Page class.
    
    A Page object is returned by each search on the piratebay website,
    it lets you easily handle all the data. Each item returned by either
    all() or search() is a list of dictionary objects, that have these
    keys:
        * name = Name of the torrent.
        * torrent-info-url = (Full) url to the torrent info page.
        * torrent-url = (Full) url to the torrent file.
        * magnet-url = (Full) url to the magnet file.
        * user = (Full) url to the user page(shows all releases by the user).
        * seeders = Amount of people seeding the torrent.
        * leechers = Amount of people leeching the torrent.
    
    So to print all torrent-urls followed by the uploader you could do this:
        >>> from piratebay.page import search_main
        >>> page = search_main("some search term")
        >>> for row in page.all():
        ...     print "%s => %s" % (row["torrent-url"], row["user"])
    """

    def _process_document(self):
        """Updates the current document. INTERNAL USE ONLY!"""
        try:
            self.current_page, self.max_page = find_number_of_pages(self.document)
        except exceptions.ElementNotFound as err:
            self.current_page, self.max_page = 0,0
        self.list_of_rows = []
        table = find_table(self.document)
        for row in process_all_rows(table):
            self.list_of_rows.append(PageItem(row))

class UserPage(BasePage):

    def _process_document(self):
        """Updates the current document. INTERNAL USE ONLY!"""
        try:
            self.current_page, self.max_page = find_number_of_pages(self.document)
        except exceptions.ElementNotFound as err:
            self.current_page, self.max_page = 0,0
        self.list_of_rows = []
        table = find_table(self.document)
        for row in process_all_rows(table, row_processor=process_user_row):
            self.list_of_rows.append(PageItem(row))