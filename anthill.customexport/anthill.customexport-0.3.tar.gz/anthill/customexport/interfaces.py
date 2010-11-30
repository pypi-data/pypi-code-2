from zope.interface import Interface

class ICustomFolderExport(Interface):
    """ Exports the contents of a custom folder to the filesystem """

    def export(path):
        """ Exports all files to the given path """
