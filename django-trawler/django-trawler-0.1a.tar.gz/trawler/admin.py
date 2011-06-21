from django.contrib import admin
from trawler.models import Campaign, Target

class TargetInline(admin.TabularInline):
    model = Target

class CampaignAdmin(admin.ModelAdmin):

    list_display = ['title', 'created', 'updated']
    date_hierarchy = 'created'
    actions = ['send_test_email', 'launch_campaign']

    inlines = [TargetInline, ]

    def send_test_email(self, request, queryset):
        # target with pk=0 means we're testing. Hits should not be counted.
        tmp_target = Target(email=request.user.email, pk=0)
        # TODO: figure out a way to pass in extra_context values for this test 
        for campaign in queryset:
            tmp_target.campaign = campaign
            tmp_target.dispatch()

        stuff = 'email'
        count = queryset.count()
        if count > 1:
            stuff = 'emails'

        self.message_user(request, "%d test %s sent to %s" % \
                          (count, stuff, request.user.email))

    def launch_campaign(self, request, queryset):
        [campaign.bulk_dispatch() for campaign in queryset]

        stuff = 'campaign'
        count = queryset.count()
        if count > 1:
            stuff = 'campaigns'

        self.message_user(request, "%d %s launched. Game on!" % (count, stuff))

admin.site.register(Campaign, CampaignAdmin)
