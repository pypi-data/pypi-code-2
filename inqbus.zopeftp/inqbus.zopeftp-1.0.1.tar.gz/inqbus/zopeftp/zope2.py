import ftp_patch


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    ftp_patch.patch_ftpserver()
