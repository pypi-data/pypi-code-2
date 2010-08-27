#encoding:utf-8

def memorise_last_page(view_func):
    """Memorise in the user session the last accessed page before entering in a view."""
    def modified_function(request, *args, **kwargs):
        request.session['last_page'] = request.get_full_path()
        request.session.modified = True
        return view_func(request, *args, **kwargs)
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def memorise_last_rendered_page(view_func):
    """Memorise in the user session the last rendered page returned by a response."""
    def modified_function(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        request.session['background_page'] = response._container[0]
        request.session.modified = True
        return response
    modified_function.__doc__ = view_func.__doc__
    return modified_function
