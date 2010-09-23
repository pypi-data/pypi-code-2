### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of new skin interface

$Id: interfaces.py 52563 2009-02-11 20:08:27Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52563 $"

from zope.app.rotterdam import Rotterdam
from zope.interface import Interface

class AuthSkin(Interface) :
    """ Skin with auth forms """

class CommunitySkin(Interface) :
    """ Skin with community components """

class CommentSkin(Interface) :
    """ Skin with comments enables """
    
class RubricatorSkin(Interface) :
    """ Skin with rubricator enabled """    

class RemotefsSkin(Interface) :
    """ Skin with remotefs components """    

class BaseSkin(Interface) :
    """ Basic Skin """
    
class NGBaseSkin(BaseSkin, RubricatorSkin, Rotterdam) :
    """ Basic skin with Rotterdam """

class NGAuthBaseSkin(AuthSkin,NGBaseSkin) :
    """ Basic skin with Rotterdam and auth """    
    
