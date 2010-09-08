from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext




def base(request, identifier, **kwargs):
    kwargs.setdefault('template_name','jqtouch/base.html')
    kwargs.setdefault('ajax_template_name','jqtouch/ajax.html')
    kwargs.setdefault('template_loader', loader)
    kwargs.setdefault('extra_context', {})
    kwargs.setdefault('context_processors',None)
    kwargs.setdefault('template_object_name', 'panel')
    kwargs.setdefault('mimetype',None)
    kwargs.setdefault('resolvers', settings.JQTOUCH_PANEL_RESOLVERS)
    
    for resolver in kwargs['resolvers']:
        panel = resolver(identifier)
        if panel is not None:
            break
    
    if panel is None:
        raise Http404('%s does not resolve to a panel' % (str(identifier),))
    
    context = RequestContext(request, {kwargs['template_object_name']: panel,},
                             kwargs['context_processors'])
    
    for key, value in kwargs['extra_context'].items():
        if callable(value):
            context[key] = value()
        else:
            context[key] = value
    
    if request.is_ajax():
        kwargs['template_name'] = kwargs['ajax_template_name']
    
    return HttpResponse(kwargs['template_loader'].get_template(kwargs['template_name']).render(context),
                        mimetype=kwargs['mimetype'])
