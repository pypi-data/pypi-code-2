from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from tinyimages.models import TinyImage, TinyFile
from tinyimages.forms import TinyImageForm, TinyFileForm


def base_list(request, form_class, model_class, template_name):
    user = request.user
    message = None
    if not user.is_authenticated():
        user = None

    if request.method == 'POST':
        form = form_class(data=request.POST.copy(), files=request.FILES)
        if form.is_valid():
            object=form.save(commit=False)
            object.owner=user
            object.save()
            if form_class == TinyFileForm:
                message = _(u'Your file has been uploaded. ' +\
                            u'Now you can select it below to be added into editor')
            else:
                message = _(u'Your image has been uploaded. ' +\
                            u'Now you can select it below to be added into editor')
            form = form_class()
    else:
        form = form_class()

    object_list = model_class.objects.filter(owner=user).order_by('title')
    jquery_media_url = hasattr(settings, 'JQUERY_BASE_MEDIA') and \
                       '%s%s' % (settings.MEDIA_URL, settings.JQUERY_BASE_MEDIA) or \
                       '%sjs/' % settings.MEDIA_URL

    return list_detail.object_list(request, object_list,
                               allow_empty = True,
                               template_name = template_name,
                               paginate_by = 16,
                               extra_context = {'form': form,
                                                'message': message,
                                                'jquery_media_url': jquery_media_url},
                               )


def file_list(request):
    return base_list(request, form_class=TinyFileForm, model_class=TinyFile, template_name='tinyimages/file_list.html')


def image_list(request):
    return base_list(request, form_class=TinyImageForm, model_class=TinyImage, template_name='tinyimages/image_list.html')


@login_required
def base_delete(request, object, template_name):
    user = request.user
    if not user.is_superuser or not user == object.owner:
        raise Http404

    if request.method == 'POST':
        if request.POST.get('yes', None):
            object.delete()
        return HttpResponseRedirect('../..')

    return render_to_response(template_name,
                              {'object': object},
                              context_instance=RequestContext(request))


def image_delete(request, image_id):
    image = get_object_or_404(TinyImage, id=image_id)
    return base_delete(request, image, template_name='tinyimages/image_delete.html')


def file_delete(request, file_id):
    file = get_object_or_404(TinyFile, id=file_id)
    return base_delete(request, file, template_name='tinyimages/file_delete.html')


def file_upload_view(request):
    return render_to_response('tinyimages/file.html',
                              {'TINYMCE_MEDIA': settings.TINYMCE_MEDIA},
                              context_instance=RequestContext(request))
