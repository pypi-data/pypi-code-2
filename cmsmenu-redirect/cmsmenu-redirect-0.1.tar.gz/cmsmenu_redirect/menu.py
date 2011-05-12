from django.contrib.sites.models import get_current_site
from django.contrib.redirects.models import Redirect

from menus.base import Modifier, NavigationNode
from menus.menu_pool import menu_pool



class RedirectModifier(Modifier):
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        site = get_current_site(request)
        
        for node in nodes:
            if isinstance(node, NavigationNode):
                try:
                    redirect = Redirect.objects.get(site=site,
                                                    old_path=node.get_absolute_url())
                    node.url = redirect.new_path
                except Redirect.DoesNotExist:
                    pass
        
        return nodes

menu_pool.register_modifier(RedirectModifier)
