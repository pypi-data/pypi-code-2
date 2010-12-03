from routes.util import RoutesException
from formencode.api import Invalid
from rum.genericfunctions import AmbiguousMethods, NoApplicableMethods

class RumException(StandardError): pass
class ConfigError(RumException): pass

class NoTemplateDefined(LookupError, RumException): pass
class NoRequest(RumException): pass

class RepositoryException(RumException): pass
class BadId(RepositoryException): pass
class ObjectNotFound(LookupError, RepositoryException): pass
class InvalidData(Invalid, RumException): pass

class SecurityDenial(RumException): pass
