from zope import schema
from zope.interface import Interface

#from zope.app.container.constraints import contains
#from zope.app.container.constraints import containers

from betahaus.memberprofile import MemberProfileMessageFactory as _

class IMemberProfile(Interface):
    """Member profile content type"""
