import logging

def migrateTo06(context):
    """Method to separate keywords by type of event.
    This method is used as upgrade step, 'context' is portal_setup."""
    
    logger=logging.getLogger('redturtle.imagedevent')
    
    brains = context.portal_catalog(portal_type="Event")
    
    for brain in brains:
        event_obj=brain.getObject()
        event_obj.setSubject('')
        event_obj.reindexObject(idxs=['Subject'])
    
    logger.info("Remove keywords 'type of event' from the categories.")