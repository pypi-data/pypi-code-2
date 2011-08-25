# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles

# Basic permissions
from Products.CMFCore import permissions

setDefaultRoles("Enable Monet Googlemaps viewlet", ('Manager',))


