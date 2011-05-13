from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from sets import Set

from Products.PloneServicesCenter.content import country


servicesFolderSchema = atapi.BaseFolderSchema + atapi.Schema((

    ))


class BaseServicesFolder(atapi.BaseFolder):
    """
    Base class for services
    """
    schema = servicesFolderSchema
    global_allow = 1

    allow_discussion = False

    def _getSomethingInSection(self, what, section_object):
        """
        For a section object (like a BuzzFolder), return the
        something (industries, countries) actually used in that section.
        """

        result = Set()
        catalog = getToolByName(self, 'portal_catalog')
        objs = catalog(path='/'.join(section_object.getPhysicalPath()))
        for o in objs:
            item = getattr(o, what, None)
            if item:
                if isinstance(item, tuple):
                    item = item[0]
                result.add(item)
        result = list(result)
        result.sort()
        return result

    def getIndustriesInSection(self, section_object):
        """
        For a section object (like a BuzzFolder), return the
        industries actually used in that section.
        """
        return self._getSomethingInSection("getIndustry", section_object)

    def getCountriesInSection(self, section_object):
        """
        For a section object (like a BuzzFolder), return the
        countries actually used in that section.
        """
        return self._getSomethingInSection("getCountry", section_object)

    def getIndustriesInThisSection(self):
        return self.getCountriesInSection(self)

    def getCountriesInThisSection(self):
        return self.getCountriesInSection(self)

    def getUniqueCountries(self):
        """
        Return countries which at least one content of the web site
        relates with
        """
        catalog = getToolByName(self, 'portal_catalog')
        return [c for c in catalog.uniqueValuesFor('getCountry') if c]

    def getUniqueCountriesNames(self):
        """
        Return countries which at least one content of the web site
        relates with; return a sorted list of (code, name) pairs.
        """
        countries = self.getUniqueCountries()
        countries = [(code, country.vocab.getValue(code, code))
                     for code in countries]
        countries.sort(lambda t1, t2: cmp(t1[1], t2[1]))
        return countries

    def getUniqueIndustries(self):
        """
        Return industries which at least one content of the web site
        relates with
        """
        catalog = getToolByName(self, 'portal_catalog')
        return [i for i in catalog.uniqueValuesFor('getIndustry') if i]

    def _getFilteredObjects(self, countries=None, industries=None, **kwargs):
        """
        Get objects filtered by countries/industries if asked for,
        handling some special cases
        """
        query = {}

        ## Add countries/industries, filtering out empty ones
        if countries:
            countries = [c for c in countries if c ]
            if countries:
                query["getCountry"] = countries

        if industries:
            industries = [i for i in industries if i ]
            if industries:
                query["getIndustry"] = industries

        ## Filter out empty/None arguments
        for key, value in kwargs.items():
            if value:
                query[key] = value

        catalog = getToolByName(self, 'portal_catalog')
        return catalog(**query)

    def getSitesUsingPlone(self, **kwargs):
        """
        Return brains of SiteUsingPlone, sorted alphabetically
        """
        return self._getFilteredObjects(meta_type="SiteUsingPlone",
                                        sort_on='getSortExpression',
                                        **kwargs)

    def getBuzzes(self, **kwargs):
        """
        Return brains of Buzz, sorted alphabetically
        """
        return self._getFilteredObjects(meta_type="Buzz",
                                        sort_on='effective',
                                        sort_order='reverse',
                                        **kwargs)

    def getCaseStudies(self, **kwargs):
        """
        Return brains of CaseStudy, sorted alphabetically
        """
        return self._getFilteredObjects(meta_type="CaseStudy",
                                        sort_on='getSortExpression',
                                        **kwargs)

    def getProviders(self, **kwargs):
        """
        Get filtered providers
        """
        return self._getFilteredObjects(meta_type="Provider",
                                        sort_on='getSortExpression',
                                        **kwargs)

    def getIndustryVocabulary(self):
        """
        Get the industry vocabulary
        """
        props = getToolByName(self, "portal_properties")
        industries = list(
            props.psc_properties.getProperty("industryVocabulary"))
        industries.sort()
        return industries

    def makeIndustryLinks(self, base_url, brain):
        """
        Ok, this is a helper method to make the , separated list of clickable
        industries
        """
        industries = brain.getIndustry
        if callable(industries):
            # So we can handle both brains and real objects
            industries = industries()
        links = ['<a href="%s?industries:list=%s">%s</a>' %
                 (base_url, industry, industry) for industry in industries]
        return ", ".join(links)

    def getSortedCountryPairs(self):
        """
        This method returns a list of sorted countries, with id and names
        """
        codes = self.getCountriesInThisSection()
        countries = [{"id": code,
                      "name": country.vocab.getValue(code, code) }
                     for code in codes]
        countries.sort(lambda a, b: cmp(a["name"], b["name"]))
        return countries
