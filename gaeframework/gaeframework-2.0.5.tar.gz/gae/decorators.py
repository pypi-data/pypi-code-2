from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson
from google.appengine.ext import deferred

def run(module, func, *args, **kwargs):
    func = __import__("%s.%s" % (module, func))
    func.run(*args, **kwargs)

def task(func):
    '''
    Decorate any function to run with deffered task.
    '''
    def defer(*args, **kwargs):
        deferred.defer(run, func.__module__, func.__name__, *args, **kwargs)
    defer.run = func
    return defer

def render(template=None, ajax=False):
    """
    Decorate the controller.
 
    Wrap view that return dict of variables, that should be used for
    rendering the template.
    
    Dict returned from view could contain special values:
      * return "template_name.html"
      * return "template_name.html", {dict of variables}
      * return {dict of variables}
    
    Usage:
    >> @render()
    >> def index(request):
    >>     return 'app_name/index.html', {...dict...}
    
    Usage with specified template:
    >> @render('app_name/index.html')
    >> def index(request):
    >>     return {...dict...}
    
    Usage with AJAX request to return JSON. In non AJAX request to be rendered page.
    >> @render(ajax=True)
    >> def index(request):
    >>     return {...dict...}
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            context = func(request, *args, **kwargs)
            if type(context) in (list, tuple):
                template = context[0]
                context = context[1] if len(context) > 1 else {}
            elif type(context) is dict:
                pass
            else:
                return context
            
            if ajax and request.is_ajax():
                return HttpResponse(simplejson.dumps(context),
                                    mimetype='application/json')
            
            return render_to_response(template, context,
                                      context_instance = RequestContext(request))
        return wrapper
    return decorator