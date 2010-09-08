from jqtouch.models import Panel

def panel_model_resolver(identifier):
    try:
        return Panel.objects.get(identifier=identifier)
    except Panel.DoesNotExist:
        return None
