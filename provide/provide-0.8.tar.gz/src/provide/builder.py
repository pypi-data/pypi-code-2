import dm.builder
from dm.ioc import *

class ApplicationBuilder(dm.builder.ApplicationBuilder):
    """
    Extends core builder by adding new application features, and by overriding
    core features with replacements for, or extensions of, core features.
    """

    #
    # Add features.
    
    def construct(self):
        super(ApplicationBuilder, self).construct()
        # todo: remove the UrlBuilderProject code
        #features.register('UrlBuilderProject', self.findUrlBuilderProject())
        features.register('PurposeLocator', self.findPurposeLocator())

    def findUrlBuilderProject(self):
        import provide.url
        return provide.url.UrlBuilderProject()
 
    def findPurposeLocator(self):
        dictionary = RequiredFeature('SystemDictionary')
        from provide.dictionarywords import DISTINGUISH_MODE, DOMAIN_NAME
        modeValue = dictionary[DISTINGUISH_MODE]
        if modeValue == 'auto':
            domainName = dictionary[DOMAIN_NAME]
            if domainName[0:8] == 'provide.':
                from provide.locator import DomainPurposeLocator
                locatorClass = DomainPurposeLocator
            else:
                from provide.locator import PathPurposeLocator
                locatorClass = PathPurposeLocator
        elif modeValue == 'path':
            from provide.locator import PathPurposeLocator
            locatorClass = PathPurposeLocator
        elif modeValue == 'domain':
            from provide.locator import DomainPurposeLocator
            locatorClass = DomainPurposeLocator
        else:
            msg = "Not a valid '%s' value: %s" % (DISTINGUISH_MODE, modeValue)
        return locatorClass()
 
    #
    # Replace features.

    def findSystemDictionary(self):
        import provide.dictionary
        return provide.dictionary.SystemDictionary()

    def findModelBuilder(self):
        import provide.dom.builder
        return provide.dom.builder.ModelBuilder()

    def findCommandSet(self):
        import provide.command
        return provide.command.__dict__

    def findFileSystem(self):
        import provide.filesystem
        return provide.filesystem.FileSystem()

    def findAccessController(self):
        import provide.accesscontrol
        return provide.accesscontrol.AccessController()

