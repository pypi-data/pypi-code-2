import HTMLParser

class TagParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.tags = set()
    
    def handle_starttag(self, tag, attrs):
        if tag not in self.tags:
            self.tags.add(tag)
    
    def getTags(self):
        self.close()
        return self.tags
