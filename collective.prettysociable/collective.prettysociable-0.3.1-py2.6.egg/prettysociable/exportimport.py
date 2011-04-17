from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPropertiesTool

# Properties are defined here, because if they are defined in
# propertiestool.xml, all properties are re-set the their initial state if you
# reinstall product in the quickinstaller.

_PROPERTIES = [
    # global properties
    dict(name='enable_default', type_='boolean', value=True),
    dict(name='enable_h1', type_='boolean', value=True),
    dict(name='speed', type_='string', value='normal'),
    dict(name='opacity', type_='float', value=0.80),
    dict(name='hide_flash', type_='boolean', value=False),
    dict(name='hover_padding', type_='int', value=0),
    dict(name='image_height', type_='int', value=70),
    dict(name='image_width', type_='int', value=70),

    # websites
    dict(name='facebook_active', type_='boolean', value=True),
    dict(name='facebook_encode', type_='boolean', value=True),
    dict(name='twitter_active', type_='boolean', value=True),
    dict(name='twitter_encode', type_='boolean', value=True),
    dict(name='delicious_active', type_='boolean', value=True),
    dict(name='delicious_encode', type_='boolean', value=True),
    dict(name='digg_active', type_='boolean', value=True),
    dict(name='digg_encode', type_='boolean', value=True),
    dict(name='linkedin_active', type_='boolean', value=True),
    dict(name='linkedin_encode', type_='boolean', value=True),
    dict(name='reddit_active', type_='boolean', value=True),
    dict(name='reddit_encode', type_='boolean', value=True),
    dict(name='stumbleupon_active', type_='boolean', value=True),
    dict(name='stumbleupon_encode', type_='boolean', value=False),
    dict(name='tumblr_active', type_='boolean', value=True),
    dict(name='tumblr_encode', type_='boolean', value=True),
]


def configureKupu(kupu):
    paragraph_styles = list(kupu.getParagraphStyles())

    new_styles = [
        ('prettySociable', 'prettySociable Link|a'),
    ]
    to_add = dict(new_styles)

    for style in paragraph_styles:
        css_class = style.split('|')[-1]
        if css_class in to_add:
            del to_add[css_class]

    if to_add:
        paragraph_styles += ['%s|%s' % (v, k) for k, v in new_styles if \
                             k in to_add]
        kupu.configure_kupu(parastyles=paragraph_styles)



def import_various(context):
    if not context.readDataFile('collective.prettysociable.txt'):
        return

    site = context.getSite()

    # Skip kupu configuration on sites that don't have kupu installed
    kupu = getToolByName(site, 'kupu_library_tool', None)
    if kupu is not None:
        configureKupu(kupu)

    # Define portal properties
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.prettysociable_properties

    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'],
                                     prop['type_'])
