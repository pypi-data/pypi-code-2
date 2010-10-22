from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('medialog.googlefonts')

class IGooglefontsConfiguration(Interface):
  """This interface defines the configlet for Googlefonts."""

  googlefonts = schema.ASCIILine(title=_(u"googlefonts", default=u'Googlefonts on'),
                              description=_(u"googlefonts_on",
                                            default=u'The divs or classes to put googlefont on.'),
                              required=True,
                              default="")
                              
  googlefontfamily = schema.Choice(title=u"Font", description=u"The Font that should be used.", values=['Cardo','Crimson Text', 'Cuprum',  'Droid Sans', 'Droid Sans Mono', 'Droid Serif',  'Inconsolata', 'Josefin Sans Std Light',   'Lobster', 'Molengo', 'Neuton', 'Nobile', 'Old Standard TT', 'PT Sans Narrow', 'PT Sans',   'Philosopher',   'Reenie Beanie',   'Tangerine',  'Vollkorn', 'Yanone Kaffeesatz', 'Cantarell'], default='Yanone Kaffeesatz')

  googlefontfamilysize = schema.ASCIILine(title=_(u"label_googlefontfamily", default=u'Size of the font'),
                              description=_(u"help_googlefontfamily", default=u''),
                              required=False,
                              default="")                         

  googlefontcss = schema.ASCIILine(title=_(u"label_googlefontcss", default=u'Extra for css. No typos please....'),
                              description=_(u"help_googlefontcss", default=u''),
                              required=False,
                              default="")     

  extracss = schema.ASCII(title=_(u"label_extracss", default=u'Extra css. Include classes and divs. No typos please....'),
                              description=_(u"help_extracss", default=u''),
                              required=False)    

class IGooglefontsLayer(Interface):
    """
    marker interface for googlefont layer
    """