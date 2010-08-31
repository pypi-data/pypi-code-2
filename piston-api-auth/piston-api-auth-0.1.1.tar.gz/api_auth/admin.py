from django.contrib import admin
from django.conf.urls.defaults import patterns
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.core import urlresolvers
from api_auth.models import Nonce

class NonceAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('value', 'consumer_key', 'timestamp', 'status')
    readonly_fields = ('value', 'consumer_key', 'timestamp')
    list_per_page = 50
    ordering = ('timestamp',)

    def __init__(self, *args, **kwargs):
        super(NonceAdmin, self).__init__(*args, **kwargs)
        # This hack removes all links from the change list.
        self.list_display_links = (None, )

    def get_urls(self):
        """
        Adds a new url for the "remove old nonces" action.
        There is a custom button for this action in the admin. ;-)
        """
        urls = super(NonceAdmin, self).get_urls()
        return patterns('',
            (r'^delete-old-nonces/$',
            self.admin_site.admin_view(self.delete_old_nonces)),
        ) + urls

    def delete_old_nonces(self, request):
        """
        Delete the old nounces (all nonces that are older than
        API_AUTH_TIMEOUT seconds).
        """
        Nonce.objects.delete_old()
        change_list = urlresolvers.reverse('admin:api_auth_nonce_changelist')
        return HttpResponseRedirect(change_list)

    # Restrict curious users.
    def restrict_courious(*args, **kwargs):
        return HttpResponseNotFound("This action is disabled.")

    add_view = delete_view = change_view = restrict_courious

admin.site.register(Nonce, NonceAdmin)
