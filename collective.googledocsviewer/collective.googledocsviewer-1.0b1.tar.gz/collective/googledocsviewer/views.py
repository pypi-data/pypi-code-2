from urllib import urlencode
from zope import schema
from zope import interface
from Products.Five import BrowserView
from collective.configviews import ConfigurableBaseView

IFRAME_SRC="http://docs.google.com/viewer?"

class IGoogleDocsViewerSettings(interface.Interface):
    """Settings"""
    
    cssstyle = schema.ASCII(title=u"CSS Style",
                            default='border: none;')
    width = schema.ASCIILine(title=u"Width",
                             default='620')
    height = schema.ASCIILine(title=u"Height",
                              default='620')

class GoogleDocsViewerView(ConfigurableBaseView):
    """View to control mimetype supported by the google doc viewer"""
    settings_schema = IGoogleDocsViewerSettings

    def validate(self):
        return True

    def file_url(self):
        return self.context.absolute_url()
    
    def iframe_src(self):
        query = {}
        query['embedded'] = True
        query['url'] = self.file_url()
        return IFRAME_SRC+urlencode(query)

    def iframe_style(self):
        return self.settings['cssstyle']

    def width(self):
        return self.settings['width']
    
    def height(self):
        return self.settings['height']

