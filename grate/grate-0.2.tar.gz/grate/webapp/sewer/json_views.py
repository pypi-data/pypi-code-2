import json
from django.http import HttpResponse
from decorators import restrict_http_method


@restrict_http_method('GET')
def admin_groups(request):
    user = request.user
    groups = [g.name for g in user.admin_groups()]
    return HttpResponse(json.dumps(groups), mimetype='text/json')
