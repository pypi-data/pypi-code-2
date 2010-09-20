from Products.Five import BrowserView
from urlparse import urlparse

class CSSClassProvider(BrowserView):
    
    def getColorClass(self, url):
	parsedURL =  urlparse(url)
	path = parsedURL[2]
	result = path.replace('/', ' ')
	return result
	
