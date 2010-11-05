from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='toolbar_flash_controlsbar', type_='boolean', value=False),
]

def import_various(context):
    if not context.readDataFile('collective.flowplayer_toolbar.txt'):
        return

    site = context.getSite()
    # Define portal properties
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.flowplayer_properties

    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
    
