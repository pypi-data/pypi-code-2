from Products.CMFCore.utils import getToolByName

def deleteProperties()
        properties_tool = getToolByName(self.context, 'portal_properties', None)
        if properties_tool is not None:
                references_properties = getattr(properties_tool, 'references_properties', None)
                if references_properties:
                        properties_tool.manage_delProperties('references_properties')

def setupVarious(context):
        deleteProperties()
