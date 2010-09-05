from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory(u"collective.xdv")

class ITransformSettings(Interface):
    """Transformation settings
    """
    
    enabled = schema.Bool(
            title=_(u"Enabled"),
            description=_(u"Use this option to enable or disable the theme "
                          u"globally. Note that the options will also affect "
                          u"whether the theme is used when this option is "
                          u'enabled.'),
            required=True,
            default=False,
        )
    
    domains = schema.Set(
            title=_(u"Domains"),
            description=_(u"Domains (host names) for which the theme should apply. "
                           "Should include port numbers where necessary. If virtual "
                           "hosting to a subpath, include the subpath here. Note that "
                           "'127.0.0.1' will not be styled, but 'localhost' is fine. "
                           "This is to ensure that you can always reach this screen if "
                           "things go wrong.."),
            required=False,
            default=set([u'localhost:8080']),
            value_type=schema.TextLine(title=_(u"Domain")),
        )

    theme = schema.TextLine(
            title=_(u"Theme template"),
            description=_(u"File path or URL to the theme template"),
            required=False,
        )

    rules = schema.TextLine(
            title=_(u"Rules file"),
            description=_(u"File path to the rules file"),
            required=False,
        )

    alternate_themes = schema.List(
            title=_(u"Alternate themes"),
            description=_(u"Define alternate themes and rules files depending on a given path. "
                    "Should be of a form 'path theme rules' (or 'path rules' with xdv 0.4), " 
                    "where path may use a regular expression syntax, "
                    "theme is a file path or URL to the theme template and "
                    "rule is a file path to the rules file."),
            required=False,
            value_type=schema.TextLine(title=_(u"Theme")),
        )
    
    notheme = schema.Set(
            title=_(u"Unstyled paths"),
            description=_(u"Specify paths that should not be styled. May use regular expression syntax"),
            required=False,
            default=set([u'^.*/emptypage$', 
                         u'^.*/manage$', 
                         u'^.*/manage_(?!translations_form)[^/]+$', 
                         u'^.*/image_view_fullscreen$',
                         u'^.*/referencebrowser_popup$', # Query string is not matched
                         u'^.*/error_log(/.*)?$',
                         u'^.*/aq_parent(/.*)?$',
                         u'^.*/portal_javascripts(/.*)?$', # TinyMCE
                         ]),
            value_type=schema.TextLine(title=_(u"Path")),
        )
    
    absolute_prefix = schema.TextLine(
            title=_(u"Absolute URL prefix"),
            description=_(u"Convert relative URLs in the theme file to absolute paths "
                           "using this prefix."),
            required=False,
        )
    
    extraurl = schema.TextLine(
            title=_(u"XSLT extension file"),
            description=_(u"It is possible to extend the XDV compiler using "
                          u"a custom XSLT file. If you have such a file, "
                          u"give a file path or URL to it here."),
            required=False,
        )
    
    read_network = schema.Bool(
            title=_(u"Read network"),
            description=_(u"If enabled, network (http, https) urls are "
                          u"allowed in the rules file and this config."),
            required=True,
            default=False,
        )

class IXDVLayer(Interface):
    """Browser layer used to indicate that collective.xdv is installed
    """
