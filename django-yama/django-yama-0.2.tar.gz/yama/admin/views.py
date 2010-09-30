from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from yama.models import Menu, MenuItem
from yama.utils import get_queryset
from yama.admin.forms import MenuItemForm

def valid_targets(request, menu_id, item_id):
    ''' 
        Find all the ids of valid targets for moving a menu item.

        The basic purpose is to prevent circular moves, i.e. trying to
        move an item under on of its descendants.
    '''
    item = get_object_or_404(MenuItem, pk=item_id)
    ids = [descendant.id for descendant in item.get_descendants()]
    ids.append(item.id)
    target_ids = [str(target.id) for target in MenuItem.objects.filter(menu=item.menu).exclude(id__in=ids)]
    return HttpResponse(','.join(target_ids))

def move_item(request, menu_id, item_id):
    '''
        Move an item.

        The move is performed relative to the given target.
    '''
    assert request.method == 'POST'
    item = get_object_or_404(MenuItem, pk=item_id)
    position = request.POST.get('position', None)
    target_id = request.POST.get('target_id', None)
    target = get_object_or_404(MenuItem, pk=target_id)
    item.move_to(target, position)
    top_level_items = MenuItem.objects.filter(menu=item.menu, parent__isnull=True)
    rc = RequestContext(request, {'top_level_items' : top_level_items, 'menu' : item.menu })
    return render_to_response('admin/yama/menu/item_table.html', rc)

def select_list(request, type_id):
    '''
        Display all objects of the given type that are a valid menu item target.
    '''
    content_type = get_object_or_404(ContentType, pk=type_id)
    target_type = content_type.model_class()
    queryset = get_queryset(request, target_type)
    opts = target_type._meta
    is_popup = True
    rc = RequestContext(request, locals())
    return render_to_response('admin/yama/menuitem/select_list.html', context_instance=rc)


