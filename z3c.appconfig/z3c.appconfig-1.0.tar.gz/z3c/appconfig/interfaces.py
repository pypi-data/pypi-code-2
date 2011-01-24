from zope.interface.common.mapping import IExtendedReadMapping

class IAppConfig(IExtendedReadMapping):
    """Application configuration stored in a simple dictionary.

    This concept was taken from repoze.bfg and Pylons which use a similar
    pattern to manage application configuration.
    """

    def loadConfig(filename, clear=False):
        """Load a configuration file. If clear is set to false the
        configuration will be merged into the current configuration. If clear
        is true the current configuration will be replaced."""
