from dm.ioc import RequiredFeature
from provide.dictionarywords import DOMAIN_NAME

class PurposeLocator(object):

    dictionary = RequiredFeature('SystemDictionary')

    def distinguishesDomains(self):
        return True

    def getPath(self, purpose):
        if purpose.name == 'production':
            return ""
        else:
            return "/%s" % (
                purpose.name,
            )

    def getFQDN(self, purpose):
        return "%s.%s" % (purpose.provision.name, self.getStrippedDN())

    def getStrippedDN(self):
        domainNameParts = self.getRawDN().split('.')
        if domainNameParts[0] == 'provide':
            domainNameParts.pop(0)
        return '.'.join(domainNameParts)

    def getRawDN(self):
        return self.dictionary[DOMAIN_NAME]


class PathPurposeLocator(PurposeLocator):

    def distinguishesDomains(self):
        return False

    def getPath(self, purpose):
        if purpose.name == 'production':
            return '/%s' % (
                purpose.provision.name,
            )
        else:
            return '/%s/%s' % (
                purpose.name,
                purpose.provision.name,
            )

    def getFQDN(self, purpose):
        return self.getRawDN()


class DomainPurposeLocator(PurposeLocator):

    def getPath(self, purpose):
        return ''

    def getFQDN(self, purpose):
        if purpose.name == 'production':
            return '%s.%s' % (
                purpose.provision.name,
                self.getStrippedDN()
            )
        else:
            return '%s.%s.%s' % (
                purpose.provision.name,
                purpose.name,
                self.getStrippedDN()
            )

