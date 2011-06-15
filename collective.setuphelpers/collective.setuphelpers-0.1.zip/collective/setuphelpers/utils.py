def makeFieldsInvisible(schema=None, fields=[]):
    """ Makes schemata fields respective widgets invisible in the edit form. """

    if schema is not None:
        for field in fields:
            schema[field].widget.visible = {
                'view':'visible',
                'edit':'invisible'
                }
        
