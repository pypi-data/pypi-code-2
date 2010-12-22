from Products.Five.browser  import BrowserView
from zope.interface import implements
from interfaces import IShareView

class ShareView ( BrowserView ):
    u"""This browser view is used to display the share popup
    """
    implements( IShareView )
