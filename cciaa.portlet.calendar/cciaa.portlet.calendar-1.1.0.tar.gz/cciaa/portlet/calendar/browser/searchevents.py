from Products.Five.browser import BrowserView

class SearchEventsView(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def test(self,condition, str1, str2):
        
        if condition:
            return str1
        else:
            return str2
    
    def date(self,request):
        date=request['end']['query'][0]
        date=date.strftime('%d-%m-%Y')
        return date
    
    def singolEvent(self, url):
        
        self.request.RESPONSE.redirect(url)
        return
    