from django import template

from softwarefabrica.django.director.modelmanager import ModelManager, _app_label_from_name

register = template.Library()

@register.inclusion_tag('director/tags/apps_menu.html')
def apps_menu():
    menu = []
    for app_name in ModelManager._registered_apps:
        app_label = _app_label_from_name(app_name)
        managers = ModelManager.ManagersForApp(app_name)
        managers = filter(lambda item: item.menu, managers)
        menu.append(dict(app_label=app_label, app_name=app_name, managers=managers))
    return {'menu': menu}
