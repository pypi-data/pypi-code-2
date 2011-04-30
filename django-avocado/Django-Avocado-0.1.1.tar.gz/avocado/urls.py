from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import redirect

@login_required
def test(request):
    from context import get_singleton_context
    
    with get_singleton_context("test context") as ctx:
        ctx.debug("Hello world!", user=request.user)
        u = User.objects.all()[0]
        ctx.debug("Model instance", user=request.user, instance=request.user)

        try:
            a = 0
            b = 2
            c = b / a
        except Exception, e:
            ctx.exception("Math exception: %s" % e, user=request.user, instance=request.user)

        for i in range(0, 1000):
            ctx.info("Counting #%s" % i)

        ctx.flush()
    
    return redirect(reverse('admin:index', args=[]))

from models import LogEntry

class LogEntryDetailsView(DetailView):

    queryset = LogEntry.objects.all()
    template_name = "avocado/details.html"
    context_object_name = 'log_detail'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LogEntryDetailsView, self).dispatch(*args, **kwargs)    

urlpatterns = patterns('',
    url(r'details/(?P<pk>\d+)/$', LogEntryDetailsView.as_view(), name='avocado-details'),
    url(r'test/$', test, name='test'),
)

