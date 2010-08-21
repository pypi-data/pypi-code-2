from markdown import Markdown

class Parser:
    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request
    def format(self, formatter):
        self.request.write(Markdown(self.raw).toString())