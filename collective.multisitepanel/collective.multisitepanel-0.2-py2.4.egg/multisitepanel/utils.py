def getZopeRoot(context):
    return context.restrictedTraverse('/')

def getSitesList(context):
    return context.ZopeFind(getZopeRoot(context),obj_metatypes=['Plone Site'])