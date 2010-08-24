# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
from urllib2 import unquote
from urlparse import urljoin
from piratebay import exceptions

class BaseParser(object):
    """Base parser for all specific parsers.
    
    Every parser are to derive from this, so as to keep the
    interface the same for all parsing.
    """
    def run(self):
        raise NotImplementedError

class TorrentTableParser(BaseParser):
    """TorrentTableParser
    
    The TorrentTableParser is the base-class for parsing tables on the
    Search and User page.
    """
    _xpath_table = ".//div[@id='content']/div[@id='main-content']/table[@id='searchResult']"
    _xpath_amount_of_pages = ".//div[@align='center']"
    
    def __init__(self, doc):
        self.doc = doc
        self.rows = []
    
    def find_table(self):
        """Search for the result table on any page on piratebay.

        Raise TableNotFound to indicate error.
        """
        table = self.doc.xpath(self._xpath_table)
        if len(table) <= 0:
            raise exceptions.ElementNotFound("Unable to find table")
        return table[0]
    
    def get_table_rows(self):
        """Return table rows.

        Raise InvalidTable to indicate error.
        """
        table = self.find_table()
        if table.tag != 'table':
            raise exceptions.InvalidTable("Invalid table found")
        return [row for row in table.iterchildren() if row.tag == 'tr']
    
    def process_page_numbers(self):
        """Parse the index.
        
        Parses the index from the page, that'll say the number of the page
        we're currently visiting. And the number of pages available as far
        as the index is showing.
        
        *Returns*
            tuple with (current_page, number_of_pages)
        """
        element = self.doc.xpath(self._xpath_amount_of_pages)
        def find_last_link(links):
            links.reverse()
            for link in links:
                if len(link.getchildren()) == 0:
                    return link
        def find_current_page(links):
            if element.text and element.text.strip().isdigit():
                return int(element.text.strip())
            for link in links:
                text = link.tail
                if len(text.strip()) > 0:
                    return int(unquote(text))
        if len(element) != 1:
            raise exceptions.ElementNotFound("Correct element for page numbers not found")
        element = element[0]
        a_eles = element.findall('a')
        current_page = find_current_page(a_eles)
        if len(a_eles) <= 0:
            raise exceptions.ElementNotFound("Incorrect element found")
        
        num_pages = int(find_last_link(a_eles).text_content())
        return current_page, num_pages
    
    def parse_row_columns(self, columns):
        """Parse the columns of a table row.
        
        *Returns*
            a dictionary with parsed data.
        """
        data = {}
        for ele in columns[0].iterchildren():
            if ele.tag == 'div' and ele.get('class') == 'detName':
                a = ele.find('a')
                data["torrent_info_url"] = urljoin(ele.base, a.get('href'))
                data["name"] = a.text_content()
            elif ele.tag == 'a':
                if ele.get('title') == "Download this torrent":
                    data["torrent_url"] = ele.get("href")
                elif ele.get('title') == "Download this torrent using magnet":
                    data["magnet_url"] = ele.get("href")
            elif ele.tag == 'font':
                a = ele.find('a')
                if a is None:
                    data['user'] = "Anonymous"
                else:
                    data['user'] = urljoin(ele.base, a.get('href'))
        data['seeders'] = int(columns[1].text_content().strip())
        data['leechers'] = int(columns[2].text_content().strip())
        return data
    
    def run(self):
        """Run the parser.
        
        Call the subclass _process_row() to process each row of the table, then
        append all parsed row data into a list. That will be returned with the other
        data such as current page and number of pages.
                
        *Returns*
            tuple with, (current_page, num_pages, [dict_with_row_data, ...]).
        """
        rows = self.get_table_rows()
        row_data = []
        for row in rows:
            row_data.append(self.process_row(row))
        current_page, num_pages = self.process_page_numbers()
        return current_page, num_pages, row_data
    
    def process_row(self, row):
        """Should be implemented by the subclass."""
        raise NotImplementedError

class SearchPageParser(TorrentTableParser):
    """SearchPageParser
    
    Is the specific parser for the search page. We keep this one separate
    from the user page parsing, because they differ abit yet have a huge
    similar dataset.
    """
    def process_row(self, row):
        """Process one row of the table."""
        columns = row.getchildren()[1:]
        if len(columns) != 3:
            raise exceptions.InvalidRow("Row isn't valid or it doesn't contain the columns it should.")
        return self.parse_row_columns(columns)

class UserPageParser(TorrentTableParser):
    """UserPageParser
    
    Is the specific parser for the user page.
    """
    _xpath_amount_of_pages = ".//tr/td[@colspan='9']"
    def process_row(self, row):
        """Process one row of the table."""
        columns = row.getchildren()[1:]
        if len(columns) == 3:
            return self.parse_row_columns(columns)