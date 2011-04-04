class ViewNotFoundException(Exception): pass

def _getInnerViewName(outer_view):
    """Get the name of the inner view for this object,
    the view name with _page cut off of the end.

    Returns a str
    """
    if '_page' == outer_view[-5:]:
        inner_view = outer_view[:-5]
    else:
        inner_view = outer_view
    view = ''.join(('@@', inner_view))
    return view

def extractInnerView(context):
    """Get the inner view for this context, the view
    of the item without page or Collage wrappers.

    Returns the html of that view.
    """
    view = _getInnerViewName(context.getLayout())
    try:
        return context.restrictedTraverse(view)()
    except Exception, msg1:
        #The view lookup failed, possibly because of the
        #@@ that got added to the beginning.
        #Try again, without the @@.
        #This is required for the built-in types, which
        #are not set up as Zope 3 style views.
        #If this one fails, go ahead and raise the
        #exception, with information on which view
        #failed on which object
        try:
            return context.restrictedTraverse(view[2:])()
        except Exception, msg2:
            raise ViewNotFoundException,\
                  "The view %(view)s could not be "\
                  "fetched on %(item)s (%(type)s) at "\
                  "%(location)s\n"\
                  "%(msg1)s\n%(msg2)s" %\
                  dict(view=view,
                       item=context.title_or_id(),
                       type=context.Type(),
                       location=context.absolute_url(),
                       msg1=msg1,
                       msg2=msg2)
