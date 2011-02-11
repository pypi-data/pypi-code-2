from django.http import Http404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from activitysync.models import Activity
from activitysync.paginator import InfinitePaginator

def activity(request, page="1", explicit_page_request=False):
    # Make sure page parameter is an integer
    try:
        page = int(page)
    except:
        raise Http404

    # Make sure we only have one canonical first page
    if explicit_page_request and page == 1:
        return redirect('main_activity')

    # Previous URL uses GET parameter 'page', so let's check
    # for that and redirect to new view if necessary
    if not explicit_page_request:
        try:
            requestNum = request.GET['page']
            if requestNum != None and requestNum.isdigit():
                return redirect('activity_paged', page=requestNum)
        except KeyError:
            pass
    
    activity_list = Activity.objects.published().defer("username", "author", "comments", "guid")
    paginator = InfinitePaginator(activity_list, 25)
    
    try:
        activities = paginator.page(page)
    except:
        raise Http404
        
    return render_to_response('activity.html',
                activities.create_template_context(),
                context_instance=RequestContext(request))
