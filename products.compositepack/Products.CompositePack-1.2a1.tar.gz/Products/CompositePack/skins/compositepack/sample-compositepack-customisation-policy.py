## Script (Python) "compositepack-customisation-policy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Composite Pack Customisation Policy
##
# Make a copy of this script called 'compositepack-customisation-policy'
# in any skin folder on your site and edit it to set up your own
# preferred configuration.
#
# The resulting script will be run automatically whenever the
# CompositePack product is installed or reinstalled.
from Products.CMFCore.utils import getToolByName

COMPOSABLE = (
              'MySimpleArticle',
              'ATLink',
              'ATTopic',
              'ATImage',)

VIEWLETS = {
        'topic_5_viewlet': 'Topic Top 5',
        'topic_10_viewlet': 'Topic Top 10',
        'topic_viewlet': 'Topic Content',
        'article_intro_viewlet': 'Article Introduction',
        'date_link_desc_viewlet': 'Date: Link and Description',
        'link_desc_viewlet': 'Link and Description',
        'hilite_link_desc_viewlet': 'Highlighted Link and Description',
        'image_link_desc_viewlet': 'Image: Link and Description',
        'title_image_body_viewlet': 'Title: Image and Body',
        'title_viewlet_grey': 'Grey Title',
}

LAYOUTS = [
    ('two_columns', 'Two columns', 'two_columns', True),
    ('three_columns', 'Three columns', 'three_columns', False),
    ('four_columns', 'Four columns', 'four_columns', False),
    ('table_slots', 'Table Layout', 'table_slots', False),
]

ct = getToolByName(context, 'composite_tool')

for compo in COMPOSABLE:
    if ct.isComposable(compo):
        print "%s already composable" % compo
    else:
        print "Register as composable", compo
        ct.registerAsComposable(compo)

LayoutIds = [ id for id,title,template,default in LAYOUTS ]
for layout_name in ct.layouts.objectIds():
    if not layout_name in LayoutIds:
        ct.unregisterLayout(layout_name)
        print "Removed layout",layout_name

for id,title,template,default in LAYOUTS:
    layout = ct.getLayoutById(id)
    if layout:
        print "Layout %s already registered" % title
    else:
        layout = ct.registerLayout(id, title, template)
        print "Layout %s registered" % title
        
    layout.registerForType('Navigation Page')
    if default:
        layout.setDefaultForType('Navigation Page')

for id, title in VIEWLETS.items():
    viewlet = ct.getViewletById(id)
    if viewlet:
        print "Viewlet %s already registered" % title
    else:
        ct.registerViewlet(id, title, id)
        print "Viewlet %s registered" % title

# Format: dictionary of:
#    typename: ([viewlet list], default_viewlet)
VIEWLET_INFO  = {
   '': (['link_viewlet', 'date_link_desc_viewlet',
         'hilite_link_desc_viewlet',
         'link_desc_viewlet', 'image_link_desc_viewlet',
         'title_image_body_viewlet'],
         'link_desc_viewlet'),
   'ATImage': (['image_viewlet', 'link_viewlet', 'date_link_desc_viewlet',
                'link_desc_viewlet'],
                'image_viewlet'),
   'ATTopic': (['topic_viewlet', 'topic_10_viewlet', 'topic_5_viewlet'],
               'topic_5_viewlet'),
   'CompositePack Titles':
     (['title_viewlet', 'title_viewlet_grey'],
       'title_viewlet'),
   'CompositePack Fragments':
     (['fragment_viewlet'],
       'fragment_viewlet'),
}
for typename in VIEWLET_INFO:
    viewlets, default = VIEWLET_INFO[typename]
    print "Register %s viewlets" % (typename or 'default')
    print ', '.join(viewlets)
    if typename:
        ct.setViewletsForType(typename, viewlets, default)
    else:
        ct.setDefaultViewlets(viewlets, default)

return printed
