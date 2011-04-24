"""
This module is used to identify classes.  It includes
methods that can be used to validate that the class
in question meets the expectations of the system.
"""

import logging, sys, traceback, re

from zope.interface.interface import InterfaceClass
from zope.interface.verify import verifyObject, verifyClass
from interface.base.verify import IVerifiable

def no_validity(self, cls, log):
    return True

def default_validity(clsid, cls, log, **kwargs):
    try:
        name = cls.__name__
        log.info("Performing the default validity check on the class factory %s" % (name))

        is_valid_version = version_check(cls, clsid)
        if not is_valid_version:
            return False

        is_implements_stated_interfaces = interface_check(cls)
        if not is_implements_stated_interfaces:
            return False

        log.info("%s passed the default validity check!" % (name))

        return True 

    except Exception, ex:
        log.error(ex)
        return False

def version_check(cls, clsid, log = logging.getLogger()):
    if len(cls.__version__) != 3:
        raise Exception("Version unavailable for comparison in dynamic class detail instance.")
    if len(cls.__name__) == 0:
        raise Exception("Name unavailable.")
    major, minor, revision = cls.__version__
    min_major, min_minor, min_revision = clsid.__version__
    if major < min_major:
        if minor < min_minor:
            if revision < min_revision:
                log.debug("%s Version Check Failed:  %s.%s.%s < %s.%s.%s" % (clsid.__name__,major,minor,revision,min_major,min_minor,min_revision))
                return False
    return True

def verify_iface(iface,cls,log):

    if not isinstance(iface,InterfaceClass):
        raise Exception("%s object must be of type %s" % (type(iface), InterfaceClass))

    log.info("Verifying %s on %s" % (iface,cls))
    if callable(cls):
        try:
            verifyClass(iface,cls)
            return True
        except:
            log.error("%s factory does not implement %s" % (cls,iface))
            log.error(sys.exc_info())
            raise
    else:    
        try:
            verifyObject(iface,cls)
            return True
        except:
            log.error("%s instance does not implement %s" % (cls,iface))
            log.error(sys.exc_info())
            raise

    return False 

def interface_check(cls, log = logging.getLogger()):
    """
    Confirms the class matches the new class matches the expected interface.
    """
    if not verify_iface(IVerifiable,cls,log):
        return False
    try:
        for iface in cls.__interface__:
            if not isinstance(iface,InterfaceClass):
                raise TypeError()
            if not verify_iface(iface,cls,log):
                return False
    except TypeError:
        iface = cls.__interface__
        if not isinstance(iface,InterfaceClass):
            log.error("%s %s stated interface must be of type %s" % (iface, type(iface),InterfaceClass))
            return False
        if not verify_iface(iface,cls,log):
            return False
    return True

class class_identifier(object):
    def __init__(self, path, name, maj, min, rev, validity_check_callable = no_validity, log = logging.getLogger()):
        self.log = log
        self.__name__ = name
        self.__version__ = (maj, min, rev)
        self.__path__ = path
        if not callable(validity_check_callable):
            raise Exception("Validity Check method parameter must be callable.")
        self.is_valid = validity_check_callable
    @property
    def path(self):
        return self.__path__
    @property
    def name(self):
        return self.__name__
    def __str__(self):
        return "<class_identifier, name=%s, version=%s, path=%s, is_valid=%s>" \
            % (   self.__name__         \
                , str(self.__version__) \
                , self.__path__         \
                , str(self.is_valid.__name__))

