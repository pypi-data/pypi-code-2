# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: Interfaces.py 236779 2011-04-01 05:51:02Z nilo $

from zope.interface import Interface, Attribute

class ICountry(Interface):
    """represens a country"""

    isocc = Attribute("The offical two-digit ISO country code")
    name = Attribute("The country's name, or None if unknown")


class IArea(Interface):
    """a collection of countries, semantically grouped"""

    name = Attribute("Area's name, like 'Middle east'")
    countries = Attribute("Sequence of ICountry instances")
    


class ICountryUtils(Interface):
    """A tool prodiving helper methods for ATCountryWidget"""
    
    def getCountryIsoDict():
        """returns a iso-code to name mapping
        
        returns dict-like object
        """

    def getCountryByIsoCode(cc):
        """returns a country name by the ISO-code
        
        cc: str
        returns ICountry instance
        
        NOTE: if there is no name for the given county code a country with
           isocc == name is returned
        """

    def getCountryIsoList():
        """returns a sequence of tuples (country name, country code)
        
        NOTE: the returned sequence is sorted alphabetically by country name
        
        returns sequence  
        """
       
    def listAreas(filter=None, omit=None):
        """get list of areas known to the system
       
        filter: sequence of str or None
            if filter is not None a list of isoccs is expected. The areas 
            country lists will only contain countries listed. 
        omit: sequence of str or None
            if omit is not None a list of isoccs is expected. The areas
            country list will only contain countries which are *not* listed.
            
        
        If either filter or omit is given, only non empay areas are returned.

        returns sequence of IArea instances
        """
