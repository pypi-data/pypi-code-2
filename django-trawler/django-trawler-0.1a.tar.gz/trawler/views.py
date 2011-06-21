from django.http import HttpResponse, Http404
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from trawler.models import Target, Campaign
import mimetypes

def link_hits(request, campaign_id, target_id=0):
    target_id = int(target_id)
    campaign_id = int(campaign_id)
    if target_id != 0:
        mark = Target.objects.get(pk=target_id)
        mark.link_followed = True
        mark.save()
    raise Http404()

def img_hits(request, campaign_id, target_id=0):
    target_id = int(target_id)
    campaign_id = int(campaign_id)
    if target_id != 0:
        mark = Target.objects.get(pk=target_id)
        mark.image_viewed = True
        mark.save()
        img = mark.campaign.img
    else:
        img = Campaign.objects.get(pk=campaign_id).img
    try:
        return HttpResponse(open(img.path, 'rb'),
                            mimetype=mimetypes.guess_type(img.path))
    except:
        raise Http404()


class CampaignDetailView(DetailView):
    model = Campaign
    context_object_name = 'campaign'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CampaignDetailView, self).dispatch(*args, **kwargs)
