# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.PortalTransforms.interfaces import itransform
try:
    from Products.PortalTransforms.interfaces import ITransform
except ImportError:
    ITransform = None

from pysrt import SubRipFile
from StringIO import StringIO

class SrtToHtml:
    """transform which render SubRip format to HTML"""

    __implements__ = itransform
    if ITransform:
        implements(ITransform) 

    __name__ = "srt_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/srt', 'application/x-subrip', 'text/plain',)):
        self.config = { 'inputs' : inputs, }
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name
            
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        """Convert the SubRip transcription to an HTML source
        """
        # Get acquisition context
        #context = kwargs.get('context')
        newdata = StringIO()

        fixed = orig.replace("\r\n", "\n")
        try:
            subrip = SubRipFile.open(file_descriptor=StringIO(fixed))
        except UnicodeDecodeError:
            subrip = SubRipFile.open(file_descriptor=StringIO(fixed),
                                     encoding='iso-8859-1')

        newdata.write('<dl class="subripSection">\n')
        for sr in subrip:
            newdata.write('<dt>%s &rarr; %s</dt>\n' % (sr.start, sr.end))
            newdata.write('<dd>%s</dd>\n' % (sr.text))
        newdata.write('</dl>\n')

        newdata.seek(0)
        data.setData(newdata.read().encode('utf-8'))

        return data

def register():
    return SrtToHtml()
