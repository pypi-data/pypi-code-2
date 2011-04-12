# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: CountryTool.py 236779 2011-04-01 05:51:02Z nilo $

# Zope imports
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

# Zope Products imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject

# Siblings
import zope.interface
from Interfaces import ICountry, IArea, ICountryUtils
from config import access_contents_information, manage_properties, COUNTRIES

siteencoding = 'iso-8859-15'

class Country:

    __allow_access_to_unprotected_subobjects__ = 1
    zope.interface.implements(ICountry)
    isocc = None
    name = None

    def __init__(self, isocc, name=None):
        self.isocc = isocc
        self.name = name

    def __eq__(self, other):
        if not ICountry.providedBy(other):
            return False
        return other.isocc == self.isocc
    
    def __str__(self):
        if self.name is None:
            return ''
        else:
            return self.name

    def __hash__(self):
        return hash(self.isocc)

    def __repr__(self):
        return '<Country %s>' % self.isocc

class Area:

    __allow_access_to_unprotected_subobjects__ = 1
    zope.interface.implements(IArea)

    name = None
    countries = []

    def __init__(self, name):
        self.name = name
        self.countries = []
       
    def __cmp__(self, other):
        if not IArea.providedBy(other):
            return -1
        return cmp(self.name, other.name)
        
    def __str__(self):
        return self.name

    def addCountry(self, country):
        if ICountry.providedBy(country):
            self.countries.append(country)
        else:
            raise TypeError, 'Parameter country is not implementing ICountry.'

    def delCountry(self, country):
        self.countries.remove(country)
    
    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<Area %s>' % self.name
 

class CountryUtils(UniqueObject, SimpleItem):
    """Provides support methods for the ATCountryWidget"""
    
    id = "portal_countryutils"
    meta_type = "ATCountryWidget_Utilities"
    security = ClassSecurityInfo()
    plone_tool = 1
    
    zope.interface.implements(ICountryUtils)
    
    manage_options = (
        {'label': 'Info', 'action': 'info_tab'},
        {'label': 'Countries', 'action': 'country_tab'},
    ) + SimpleItem.manage_options

    country_tab = PageTemplateFile('www/CountryUtilCountries.zpt', globals(),
                                   __name__='country_tab')
    manage_main = info_tab = PageTemplateFile('www/CountryUtilInfo.zpt',
                                              globals(), __name__='info_tab')

    _country_list = []
    _area_list = []

    def __init__(self):
        self.manage_countries_reset()

    security.declareProtected(access_contents_information, 'getCountryIsoDict')
    def getCountryIsoDict(self):
        cdict = {}
        for country in self.listCountries():
            cdict[country.isocc] = country.name
        for area in self._area_list:
            for country in area.countries:
                cdict[country.isocc] = country.name
        return cdict

    security.declareProtected(access_contents_information, 'getCountryIsoList')
    def getCountryIsoList(self):
        clist = self.getCountryIsoDict().items()
        clist.sort(lambda a,b: cmp(a[1], b[1]))
        return tuple(clist)
    
    security.declareProtected(access_contents_information,
                              'getCountryByIsoCode')
    def getCountryByIsoCode(self,cc):
        cdict = self.getCountryIsoDict()
        name = cdict.get(cc, cc)
        return Country(cc, name)

    security.declareProtected(access_contents_information, 'listCountries')
    def listCountries(self):
        """return sequence of unasigned countries"""
        return tuple(self._country_list)

    
    security.declareProtected(access_contents_information, 'listAreas')
    def listAreas(self, filter=None, omit=None):
        """list available areas"""
        assert filter is None or isinstance(filter, (tuple, list))
        assert omit is None or isinstance(omit, (tuple, list))

        if filter is None and omit is None:
            areas = self._area_list
        else:
            areas = []
            for area in self._area_list:
                a = Area(area.name)
                add = area.countries
                if filter is not None:
                    add = [ c for c in add if c.isocc in filter ]
                if omit is not None:
                    add = [ c for c in add if c.isocc not in omit ]
        
                for country in add:
                     a.addCountry(country)
                if a.countries:
                    areas.append(a)
        return tuple(areas)
    
    security.declareProtected(access_contents_information, 'getArea')
    def getArea(self, countrycode):
        """returns area name of country code"""
        for area in self.listAreas():
            if countrycode in [c.isocc for c in area.countries]:
                return area.name
        return None
                                        

    #######
    # management methods
    
    security.declareProtected(manage_properties, 'manage_countries_reset')
    def manage_countries_reset(self, REQUEST=None):
        """reset country/area lists"""
        self._country_list = []
        self._area_list = []
                
        for cc, name in COUNTRIES.items():
            c = Country(cc, name)
            self._country_list.append(c)
        self._sort_country_list()
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Reset.')

    security.declareProtected(manage_properties, 'manage_countries_addCountry')
    def manage_countries_addCountry(self, cc, name, REQUEST=None):
        """Add a new (custom) country.

        cc ... str, two digit ISO country code
        name ... str, name of country
        """
        # method is only used by Installer of products using ATCountryWidget
        c = Country(cc, name)
        self._country_list.append(c)
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Country added.')

    

    
    security.declareProtected(manage_properties, 'manage_countries_addArea')
    def manage_countries_addArea(self, area_name, REQUEST=None):
        """add a new area"""
        a = Area(area_name)
        self._area_list.append(a)
        self._p_changed = 1
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Area added')

    security.declareProtected(manage_properties,
                              'manage_counties_addCountryToArea')
    def manage_countries_addCountryToArea(self, area, ccs, REQUEST=None):
        """add country to area"""
        clist = self._country_list
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        for cc in ccs:
            c_id = clist.index(Country(cc))
            c = clist[c_id]
            del(clist[c_id])
            a.addCountry(c)
        self._p_changed = 1
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Countries added.')

    
    security.declareProtected(manage_properties, 'manage_countries_moveUpArea')
    def manage_countries_moveUpArea(self, area, REQUEST=None):
        """move area up"""
        self._move_area(area, -1)
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Area moved.')
            
    security.declareProtected(manage_properties,
                              'manage_countries_moveDownArea')
    def manage_countries_moveDownArea(self, area, REQUEST=None):
        """move area up"""
        self._move_area(area, 1)
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Area moved.')


    security.declareProtected(manage_properties, 'manage_countries_deleteArea')
    def manage_countries_deleteArea(self, area, REQUEST=None):
        "remove area"
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        del(alist[a_id])
        for c in a.countries:
            self._country_list.append(c)
        self._sort_country_list()
        self._p_changed = 1
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message=
                'Removed area. Countries are back in the right list.')


    security.declareProtected(manage_properties,
                              'manage_countries_moveUpCountry')
    def manage_countries_moveUpCountry(self, area, country, REQUEST=None):
        "move country up"
        self._move_country(area, country, -1)
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Country moved.')


    security.declareProtected(manage_properties,
                              'manage_countries_moveDownCountry')
    def manage_countries_moveDownCountry(self, area, country, REQUEST=None):
        "move country down"
        self._move_country(area, country, 1)
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message='Country moved.')

        
    security.declareProtected(manage_properties,
                              'manage_countries_deleteCountryFromArea')
    def manage_countries_deleteCountryFromArea(self, area, country,
            REQUEST=None):
        "remove country from area"
        self._remove_country(area, country)
        self._sort_country_list()
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message=
                'Removed country from area. Country is back in the '
                'right list.')

    security.declareProtected(manage_properties, 'manage_countries_sortArea')
    def manage_countries_sortArea(self, area, REQUEST=None):
        """sort area's countries by name"""
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        a.countries.sort(lambda a, b: cmp(a.name, b.name))
        if REQUEST is not None:
            return self.country_tab(manage_tabs_message=
                'Countries sorted.')


    
    security.declareProtected(manage_properties, 'manage_generate_po_template')
    def manage_generate_po_template(self, REQUEST=None):
        """generate .po tempalte"""
        areas = self.listAreas()
        ret = []
        ret.append('# areas')
        for area in areas:
            ret.append('msgid "'+area.name.strip()+'"')
            ret.append('msgstr "'+area.name.strip()+'"')
            ret.append('')
        
        ret.append('# countries')
        for area in areas:
            for country in area.countries:
                ret.append('msgid "'+country.name.strip()+'"')
                ret.append('msgstr "'+country.name.strip()+'"')
                ret.append('')

        return '\n'.join(ret)
    
    #########
    # private

    security.declarePrivate('_sort_country_list')
    def _sort_country_list(self):
        self._country_list.sort(lambda x,y: cmp(x.name, y.name))
        self._p_changed = 1

    security.declarePrivate('_move_area')
    def _move_area(self, area, direction):
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        del(alist[a_id])
        alist.insert(a_id + direction, a)
        self._p_changed = 1 

    security.declarePrivate('_move_country')
    def _move_country(self, area, isocc, direction):
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        countries = a.countries
        c_id = countries.index(Country(isocc))
        c = countries[c_id]
        del(countries[c_id])
        countries.insert(c_id + direction, c)
        self._p_changed = 1 

    security.declarePrivate('_remove_country')
    def _remove_country(self, area, isocc):
        alist = self._area_list
        a_id = alist.index(Area(area))
        a = alist[a_id]
        countries = a.countries
        c_id = countries.index(Country(isocc))
        c = countries[c_id]
        del(countries[c_id])
        self._country_list.append(c)
        self._p_changed = 1

            
InitializeClass(CountryUtils)

def manage_addCountryUtils(dispatcher, REQUEST=None):
    "add CountryUtils"
    util = CountryUtils()
    dispatcher._setOb(util.id, util)
    util = getattr(disptacher, util.id)
    if REQUEST is not None:
        return util.manage_main()

