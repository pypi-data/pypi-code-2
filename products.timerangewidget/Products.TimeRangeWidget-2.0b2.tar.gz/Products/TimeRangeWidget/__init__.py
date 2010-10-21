from Products.validation import validation
from Products.CMFCore import utils, DirectoryView
from Products.TimeRangeWidget.config import *

from validator import TimeRangeValidator
validation.register(TimeRangeValidator('isValidTimeRange', title='', description=''))

DirectoryView.registerDirectory('skins', product_globals)