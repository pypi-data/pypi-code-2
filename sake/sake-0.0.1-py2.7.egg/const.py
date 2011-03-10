""" This is where the general purpose sake-level constants are placed for use by sake, or any deriving application."""

# Process constants
WAIT_INFINITE           = -1
""" Passed to waiting functionality to indicate that it should wait until events occur, and not time out. """
WAIT_CHECK              = 0
""" Passed to waiting functionality to poll whether it would wait (but does not actually incur the wait that would otherwise be done). """


# Service and session roles (somewhat borrowed from EVE)
ROLE_ANY                = 0x0000000000000000L  # No authentication required. Any session role will do (even zero).
""" A general session role mask which indicates that the session no role. """
ROLE_USER               = 0x0000000000000001L  # Authentication required. Session has at least a valid userid.
""" A general session role mask which indicates that the session is an authenticated normal user. """
ROLE_ADMIN              = 0x0000000000000020L  # Administrator
""" A general session role mask which indicates that the session is an authenticated administrative user. """
ROLE_SERVICE            = 0x0000000000000040L
""" A general session role mask which indicates that the session is a framework service. """
ROLE_NOACCESS           = 0xFFFFFFFFFFFFFFFFL
""" A general session role mask which indicates inaccessibility. """


# Application roles.
APP_ROLE_UNKNOWN        = 0x0000000000000000L
""" A general application role mask which indicates that the running application doesn't know what it is. """
APP_ROLE_CLIENT         = 0x0000000000000001L
""" A general application role mask which indicates that the running application operates in a client capacity. """
APP_ROLE_SERVER         = 0x0000000000000002L
""" A general application role mask which indicates that the running application operates in a server capacity. """
# The bits which are for use for what purpose.
APP_ROLE_MASK_SAKE      = 0x00000000FFFFFFFFL
""" A general application role mask which indicates the bits reserved for use by sake and not encompassing applications. """
APP_ROLE_MASK_APP       = 0xFFFFFFFF00000000L
""" A general application role mask which indicates the bits reserved for encompassing applications. """


# Platform string constants
PLATFORM_WIN32          = "win32"
""" The value of :literal:`sys.platform` when an application is run on a Windows platform. """
PLATFORM_PS3            = "PS3"
""" The value of :literal:`sys.platform` when an application is run on a PS3 platform. """
