
class ValidationError(Exception):
    """Base class for all expected errors that we find. Don't print a stack trace
    for these.
    """
    pass

class FileFormatError(ValidationError):
    pass

class FileMissingError(ValidationError):
    pass

class ArchiveStructureError(ValidationError):
    pass

class SettingsImportError(ValidationError):
    """Error when trying to import the django settings file"""
    pass

class TestSetupError(ValidationError):
    """This exception is thrown when there is a problem with setting up the tests,
    not necessarily with the application itself.
    """
    pass

class VersionError(ValidationError):
    """This error is signaled when the version of the packager used to package the app is
    obsolete.
    """
    pass