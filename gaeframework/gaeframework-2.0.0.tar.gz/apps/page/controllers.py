from django.template import TemplateDoesNotExist

def render(app, template):
    try:
        return app.render("page/%s" % template)
    except TemplateDoesNotExist, e:
        app.error(404)
        return ""