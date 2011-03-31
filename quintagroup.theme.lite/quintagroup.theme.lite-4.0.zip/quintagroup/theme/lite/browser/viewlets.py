from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from plone.app.layout.viewlets import common

class SearchBoxViewlet(common.SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
class PersonalBarViewlet(common.PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/personal_bar.pt')
