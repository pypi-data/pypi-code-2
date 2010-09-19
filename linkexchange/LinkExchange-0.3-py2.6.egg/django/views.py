from django.http import Http404, HttpResponse

from linkexchange.django import support

def handle_request(request):
    if support.platform is None:
        raise Http404

    page_request = support.convert_request(request)
    page_response = support.platform.handle_request(page_request)

    if page_response.status == 404 and not page_response.body:
        raise Http404

    headers = page_response.headers.copy()
    response = HttpResponse(page_response.body,
            content_type=headers.pop('Content-Type', 'text/html'),
            status=page_response.status)
    for k, v in headers.items():
        response[k] = v

    return response
