def shortlink( request ):
    """
    Context Processor provides the shortlink URL to the view as SHORTLINK.
    """

    c = {
        'SHORTLINK' : request.META['shortlink'] ,
    }
    
    return c