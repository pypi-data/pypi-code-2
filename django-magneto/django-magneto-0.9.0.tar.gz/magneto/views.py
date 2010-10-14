from django.contrib.sites.models import Site
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Template


def detail(request, name):
    """
    Render a page for a ``Template`` object that matches the current
    site and ``name`` keyword argument. If no matching ``Template``
    is found or if the ``Template`` is not marked as ``visible``,
    raise a 404.
    
    The content type of the response corresponds to the content_type
    field of the ``Template`` object.

    **Required arguments**

        ``name``
            The name of the ``Template`` object to match.

    **Context**

        ``template``
            The ``Template`` object being rendered.
    """

    try:
        template_instance = Template.objects.get(
            name=name,
            visible=True,
            site=Site.objects.get_current(),
        )
    except Template.DoesNotExist:
        raise Http404

    return render_to_response(
        template_instance.name,
        dict(template=template_instance),
        context_instance=RequestContext(request),
        # KLUDGE: Coerce the content_type field from unicode to string.
        # Otherwise, Apache and nginx seem to have random issues with
        # interpreting the content type.
        mimetype=str(template_instance.content_type),
    )
