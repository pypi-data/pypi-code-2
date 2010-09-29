# -*- coding: latin-1 -*-

"""instrospection -  this module provides helper function related with introspection functionality

@author: Adrián Deccico
"""

def isSomething(obj, specific_type):
    """return True if the argument is a valid something, according to type"""
    return specific_type in str(type(obj))

def isInstance(obj):
    """return True if the argument is a valid instance of any object"""
    return isSomething(obj, "instance")

def isList(lst):
    """return True if the argument is a valid list"""
    return isSomething(lst, "list")

def isInt(number):
    """return True if the argument is a valid integer"""
    return isSomething(number, "int")

def isBool(boolean):
    """return True if the argument is a boolean"""
    return isSomething(boolean, "bool")
    