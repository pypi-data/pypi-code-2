import os
from zLOG import LOG, INFO
from Globals import package_home

from Products.CMFCore.utils import getToolByName
from ZPublisher.HTTPRequest import record

product_globals = globals()

def setupExtraCatalogIndex(context):
    """
    well, catalog.xml does not support to set up more than one catalog in it
    """
    catalog = getToolByName(context, 'portal_catalog')
    sfq_catalog = getToolByName(context, 'portal_sfq_catalog')
    sfq_indexes = sfq_catalog.indexes()
    indexes = [(index_name, index_object.meta_type, index_object) for index_name, index_object in
            catalog._catalog.indexes.iteritems()]
    catalog_lexicons = [cat_attr for cat_attr in dir(catalog) if cat_attr.endswith('_lexicon')]
    sfq_lexicons = [cat_attr for cat_attr in dir(sfq_catalog) if cat_attr.endswith('_lexicon')]
    for cat_attr in catalog_lexicons:
        if cat_attr not in sfq_lexicons:
            setattr(sfq_catalog, cat_attr,  getattr(catalog, cat_attr))
    #Create index and metadata for catalog from the portal catalog 
    for name, meta_type, index_object in indexes:
        if name not in sfq_indexes:
            if meta_type not in ['ZCTextIndex']:
                sfq_catalog.addIndex(name, meta_type)
                sfq_catalog.addColumn(name=name)
            else:
                zcti_extra = record()
                zcti_extra.lexicon_id = index_object.lexicon_id
                zcti_extra.index_type = 'Okapi BM25 Rank'
                zcti_extra.doc_attr   = name
                sfq_catalog.addIndex(name, meta_type, zcti_extra)
                sfq_catalog.addColumn(name=name)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('collective.salesforce.query_various.txt') is None:
        return

    site = context.getSite()
    LOG('collective.salesforce.query', INFO, 'calling setup_skin_layers')
    setupExtraCatalogIndex(site)
    LOG('collective.salesforce.query', INFO, 'Finished with Extra Catalog Index')
    setup_skin_layers(site)
    LOG('collective.salesforce.query', INFO, 'Finished with setupVarious')



skin_order = ['custom','salesforce_query_custom']
def setup_skin_layers(site):
    skin_paths = site.portal_skins._getSelections()
    current_skin_name = site.getCurrentSkinName()
    current_skin = skin_paths.get(current_skin_name)
    if current_skin is not None:
        current_skin = current_skin.split(',')
        to_preppend = []
        for lay in skin_order:
            if lay in current_skin:
                current_skin.remove(lay)
            to_preppend.append(lay)
        current_skin = to_preppend + current_skin
        skin_paths[current_skin_name] = ','.join(current_skin)

