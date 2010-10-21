from Products.validation import validation
from Products.CMFCore import utils, DirectoryView
from Products.DimensionWidget.config import *

from validator import PositiveDimensionValidator
validation.register(PositiveDimensionValidator('isPositiveDimension', title='', description=''))

DirectoryView.registerDirectory('skins', product_globals)