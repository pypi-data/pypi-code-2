from django.core.urlresolvers import get_callable


def dispatcher(req, callbacks):
    """URL alternatives dispatcher that is trying given callbacks until one return success.
    
    As you can see from the following example the URL alternatives dispatcher is
    simply used as part of the `urlpatterns` variable in `urls.py` and supports
    passing of positional and keyword arguments for the given list of views, eg.:

      urlpatterns += pattern('',
          (r'^', 'urlalternatives.views.dispatcher', {'callbacks':[
              app1.views.failing404,
              'app2.views.working',
              (redirect_to, [], {'url':'/'}),
           ]}),
       )
    """
    for call in callbacks:
        args = []
        kwds = {}
        if isinstance(call, (tuple, list)):
            args = call[1]
            kwds = call[2]
            call = call[0]
        call = get_callable(call)

        response = call(req, *args, **kwds)
        if response.status_code < 400:  # accepted HTTP status codes
            break

    return response

