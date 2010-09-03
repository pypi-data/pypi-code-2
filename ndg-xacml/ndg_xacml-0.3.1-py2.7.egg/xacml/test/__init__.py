"""NDG XACML unit test package 

NERC DataGrid
"""
__author__ = "P J Kershaw"
__date__ = "16/03/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: __init__.py 7087 2010-06-25 11:23:09Z pjkersha $"
from os import path

THIS_DIR = path.dirname(__file__)
XACML_NDGTEST1_FILENAME = "ndg1.xml"
XACML_NDGTEST1_FILEPATH = path.join(THIS_DIR, XACML_NDGTEST1_FILENAME)
