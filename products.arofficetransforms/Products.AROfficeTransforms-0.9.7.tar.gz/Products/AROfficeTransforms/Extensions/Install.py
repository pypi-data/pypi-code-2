from Products.MimetypesRegistry import MimeTypeItem
from Products.CMFCore.utils import getToolByName

from Products.AROfficeTransforms.config import TRANSFORMS

def install(self):
    transform_tool = getToolByName(self, 'portal_transforms')
    for transform in TRANSFORMS:
      print "atReal : Adding %s transform" % transform
      # Remove existing transform, if any
      if transform in transform_tool.objectIds():
        transform_tool.manage_delObjects([transform])
      transform_tool.manage_addTransform(transform, 'Products.AROfficeTransforms.transforms.'+transform)
      print "atReal : %s added" % transform

def uninstall(self):
    transform_tool = getToolByName(self, 'portal_transforms')
    for transform in TRANSFORMS:
      print "atReal : Deleting %s transform" % transform
      if transform in transform_tool.objectIds():
        try:
          transform_tool.manage_delObjects([transform])
        except Exception, e:
          print e.__class__.__name__, str(e)
