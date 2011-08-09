from django.template import TemplateDoesNotExist

def render(request, template):
    try:
        return request.render("page/%s" % template)
    except TemplateDoesNotExist, e:
        request.error(404)
        return ""