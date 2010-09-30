from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_unicode
from django.conf.urls.defaults import patterns

from yama.models import Menu, MenuItem
from yama.settings import MODELS, VIEWS

from forms import MenuItemForm
from views import valid_targets, move_item, select_list

class MenuAdmin(admin.ModelAdmin):
    def get_urls(self):
        ''' Route custom URLs '''
        urls = super(MenuAdmin, self).get_urls()
        menu_urls = patterns('',
            (r'^(?P<menu_id>\d+)/item/add/$', 
                MenuItemAdmin(MenuItem, self.admin_site).add_view),
            (r'^(?P<menu_id>\d+)/item/add/as/(?P<position>[-\w]+)/of/(?P<parent_id>\d+)/$', 
                MenuItemAdmin(MenuItem, self.admin_site).add_view),
            (r'^(?P<menu_id>\d+)/item/(?P<item_id>\d+)/move/$',
                move_item),
            (r'^(?:\d+)/item/(?P<object_id>\d+)/delete/$',
                MenuItemAdmin(MenuItem, self.admin_site).delete_view),
            (r'^(?P<menu_id>\d+)/item/(?P<item_id>\d+)/valid-targets/$',
                valid_targets),

            # Happens when 
            #   -we save an item (w/o "continue editing")
            #   -delete an item
            #   -follow the breadcrumbs from the change_view of one of this menu's MenuItems
            # This should display a list of items, so we redirect to the menu
            # containing the item
                (r'^(?:.*)/item/$',
                lambda request: HttpResponseRedirect('../')),

            (r'^(?:\d+)/item/(?P<item_id>\d+)/$',
                MenuItemAdmin(MenuItem, self.admin_site).change_view),
            (r'^contenttype/(?P<type_id>\d+)/$',
                select_list),
        )
        return menu_urls + urls

    def __call__(self, request, url):
        ''' Fallback for custom URL routing for Django 1.0 '''
        if not url:
            return super(MenuAdmin, self).__call__(request, url)
        if 'item' in url:
            if 'add' in url:
                parts = url.split('/')
                menu_id = parts[0]
                if len(parts) == 3:
                    # url looks like <menu_id>/item/add
                    # Invoked by clicking "Add a new item" button at the menu level
                    # rather than the "add" button at the item level, just put it
                    # as the first root-level item
                    position = None
                    parent_id = None
                else:
                    # url looks like <menu_id>/item/add/as/<position>/of/<parent_id>
                    position = parts[-3]
                    parent_id = parts[-1]
                return MenuItemAdmin(MenuItem, self.admin_site).add_view(request, menu_id, position, parent_id)

            elif 'move' in url:
                # url looks like: <menu_id>/item/<item_id>/move/
                parts = url.split('/')
                item_id = parts[2]
                return move_item(request, item_id)

            elif 'delete' in url:
                # url looks like: <menu_id>/item/<item_id>/delete
                parts = url.split('/')
                item_id = parts[-2]
                return MenuItemAdmin(MenuItem, self.admin_site).delete_view(request, item_id)

            elif 'valid-targets' in url:
                # url looks like: <menu_id>/item/<item_id>/valid-targets
                parts = url.split('/')
                item_id = parts[2]
                return valid_targets(request, item_id)

            elif url.endswith('item'):
                # Happens when 
                #   -we save an item (w/o "continue editing")
                #   -delete an item
                #   -follow the breadcrumbs from the change_view of one of this menu's MenuItems
                # This should display a list of items, so we redirect to the menu
                # containing the item
                return HttpResponseRedirect('../')

            else:
                # url looks like <menu_id>/item/<item_id>
                # it's the change view for an item, proxy the request to MenuItemAdmin
                menu_id, dummy, item_id = url.split('/')
                return MenuItemAdmin(MenuItem, self.admin_site).change_view(request, item_id)

        elif 'contenttype' in url:
            # url looks like contenttype/<contenttype_id>
            parts = url.split('/')
            type_id = int(parts[1])
            return select_list(request, type_id)
        return super(MenuAdmin, self).__call__(request, url)

    def change_view(self, request, object_id, extra_context=None):
        try:
            obj = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None
        else:
            extra_context = {
                'top_level_items' : MenuItem.objects.filter(menu=obj, parent__isnull=True),
                'menu' : obj,
            }
        return super(MenuAdmin, self).change_view(request, object_id, extra_context)


# Item menus and parent items are handled automatically, so there's no need to
# display them. If we haven't been configured to use any models or views as
# targets, we remove the corresponding fields as well to reduce the clutter.

item_form_exclude = ['menu', 'parent']
if not MODELS:
    item_form_exclude += ['content_type', 'object_id', 'link_object']
if not VIEWS:
    item_form_exclude += ['link_view']

class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    exclude = item_form_exclude

    def add_view(self, request, menu_id, position=None, parent_id=None, *args, **kwargs):
        self._menu = get_object_or_404(Menu, pk=menu_id)
        if position:
            self._parent = get_object_or_404(MenuItem, pk=parent_id)
        else:
            self._parent = None
        self._position = position
        return super(MenuItemAdmin, self).add_view(request, *args, **kwargs)

    def change_view(self, request, item_id, extra_context=None):
        try:
            item = self.model.objects.get(pk=item_id)
        except self.model.DoesNotExist:
            item = None
        else:
            # Create a user-friendly representation of the selected object,
            # which will later be displayed in the template
            if item.link_object:
                object_repr = unicode(item.link_object)
            else:
                object_repr = ''
            extra_context = {
                'link_object_repr' : object_repr,
            }
        return super(MenuItemAdmin, self).change_view(request, item_id, extra_context)


    def save_model(self, request, obj, form, change):
        if change:
            # called from the change_view, no particular magic to be done
            obj.save()
        else:
            # called from add_view
            obj.menu = self._menu
            MenuItem._tree_manager.insert_node(node=obj, target=self._parent, position=self._position, commit=True)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        A rather simplistic response_add, redirecting only to the corresponding menu
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
          
        msg = force_unicode(_('The %(name)s "%(obj)s" was added successfully.')) % {
            'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)
        }
        if self._parent:
            return HttpResponseRedirect('../../../../../../')
        else:
            return HttpResponseRedirect('../../')


admin.site.register(Menu, MenuAdmin)
#admin.site.register(MenuItem, MenuItemAdmin)
