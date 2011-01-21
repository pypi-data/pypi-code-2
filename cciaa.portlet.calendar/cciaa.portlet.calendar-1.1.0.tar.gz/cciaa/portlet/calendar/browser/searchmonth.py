from Products.Five.browser import BrowserView
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.utils import getToolByName

PLMF = MessageFactory('plonelocales')

class SearchMonthView(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def test(self,condition, str1, str2):
        
        if condition:
            return str1
        else:
            return str2
    
    def month(self,request):
        date=request['end']['query'][0]
        month=str(date.month())
        _ts = getToolByName(self.context, 'translation_service')
        monthName = PLMF(_ts.month_msgid(month),default=_ts.month_english(month))
        return monthName
    
    def year(self,request):
        date=request['end']['query'][0]
        year=str(date.year())
        return year