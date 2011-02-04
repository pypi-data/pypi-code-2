"""System exception classes."""

# todo: Rename Kforge out of this module.

class DomainModelApplicationError(StandardError): pass

class MissingConfigurationPath(DomainModelApplicationError): pass

class ORMError(DomainModelApplicationError): pass

class InvalidSystemDictionary(DomainModelApplicationError): pass

class AccessControlException(DomainModelApplicationError): pass

class AccessIsAuthorised(AccessControlException): pass

class AccessIsForbidden(AccessControlException): pass

class DataMigrationError(DomainModelApplicationError): pass

class MissingMethodError(DomainModelApplicationError): pass

class MissingPluginSystem(DomainModelApplicationError): pass

class WebkitError(DomainModelApplicationError): pass

# todo: Rework the KForge exception classes.
class KforgeError(DomainModelApplicationError):
    "Kforge exception superclass."
    pass

class KforgeAbstractMethodError(KforgeError):
    "Unimplemented abstract method exception class."
    pass

class KforgeCommandError(KforgeError):
    "Command exception class."
    pass

class KforgePersonActionObjectDeclined(KforgeCommandError):
    "Access control denied class."
    pass
    
class KforgeRegistryKeyError(KforgeError, KeyError):
    "Registry exception class."
    pass
    
class KforgeSessionCookieValueError(KforgeError):
    "Session cookie exception class."
    pass
    
class KforgeDomError(KforgeError):
    "Domain layer exception class."
    pass

class DomainClassRegistrationError(KforgeDomError):
    "Domain class registration exception class."
    pass
    
class KforgeDbError(KforgeError):
    "Database layer exception class."
    pass

class KforgePluginMethodNotImplementedError(KforgeAbstractMethodError):
    "Missing plugin method exception class."
    pass

class MissingPluginSystem(KforgeError):
    "Missing plugin system exception."

class MultiplePluginSystems(KforgeError):
    "Multiple plugin system exception."


