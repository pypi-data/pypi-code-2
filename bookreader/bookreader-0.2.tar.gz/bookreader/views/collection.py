from django.shortcuts import get_object_or_404
from django.views.generic import list_detail

from bookreader.models import Collection



def browse(request, **kwargs):
    kwargs.setdefault('template_object_name','collection')
    kwargs.setdefault('queryset', Collection.objects.all())
    return list_detail.object_list(request, **kwargs)

def view(request, object_id, **kwargs):
    collection = get_object_or_404(Collection, pk=object_id)
    
    kwargs.setdefault('template_object_name','book')
    kwargs.setdefault('template_name', 'bookreader/collection_detail.html')
    kwargs.setdefault('queryset', collection.books.all())
    kwargs.setdefault('extra_context', {})
    kwargs['extra_context']['collection'] = collection
    
    return list_detail.object_list(request, **kwargs)
