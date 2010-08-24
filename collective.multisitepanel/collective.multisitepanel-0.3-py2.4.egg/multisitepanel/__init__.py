from zope.i18nmessageid import MessageFactory

# your.app.package must match domain declaration in .po files
MultisitePanelMessageFactory = MessageFactory('collective.multisitepanel')
  # -*- extra stuff goes here -*- 

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    pass