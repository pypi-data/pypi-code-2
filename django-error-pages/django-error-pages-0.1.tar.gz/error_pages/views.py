# from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import Context, loader

def display_error(request):
    '''Render error page for a code'''
    if 'code' in request.GET:
        try:
            code = int(request.GET['code'])
        except ValueError:
            raise ValueError("GET var 'code' must be a number")

        if code not in [400, 401, 402, 403, 404, 405, 406, 407, 408,
                        409, 410, 411, 412, 413, 414, 415, 416, 417,
                        418, 422, 423, 424, 425, 426,
                        500, 501, 502, 503, 504, 505, 507, 509, 510]:
            raise ValueError("GET var 'code' must be a valid HTTP status code")
    else:
        raise RuntimeError("GET var 'code' is missing")

    # FIXME: is setting the status code really required? wouldn't Apache
    # set it on it's own anyways??
    t = loader.get_template('%d.html' % code)
    return HttpResponse(t.render(Context({'request': request})), status=code)

#    return render_to_response('%d.html' % code,
#        context_instance=RequestContext(request)
#    )
