from django.db import models
from django.core.mail import EmailMessage, EmailMultiAlternatives
from datetime import datetime
from django.template import Context, Template

class Campaign(models.Model):
    title = models.CharField(max_length=45)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=60, blank=True,
                                   help_text='Name to display for the sender'
                                   ' (can be used to primitavely obfuscate the'
                                   ' email address)')
    subject = models.CharField(max_length=255)

    email_plain = models.TextField()
    email_html = models.TextField(blank=True)
    img = models.FileField(upload_to='uploads/%Y/%m/%d', null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return self.title

    def bulk_dispatch(self):
        [target.dispatch() for target in self.targets.all()]
        self.save() # to update the self.updated value 

    def get_percents(self):
        """
        Primitive % calculator for pass/fail.
        """
        total = self.targets.count()
        # FIXME: there's totally a divide by zero problem here.
        return dict(link=(float(self.targets.filter(link_followed=True
                                                    ).count()) / total) * 100,
                    img=(float(self.targets.filter(image_viewed=True
                                                     ).count()) / total) * 100,
                    good=(float(self.targets.filter(image_viewed=False,
                                                    link_followed=False,
                                                     ).count()) / total) * 100)


    @models.permalink
    def get_absolute_url(self):
        return ('campaign_detail', (), {'pk': self.pk})

class Target(models.Model):
    email = models.EmailField()
    campaign = models.ForeignKey(Campaign, related_name='targets')
    link_followed = models.BooleanField(default=False, editable=False)
    image_viewed = models.BooleanField(default=False, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    extra_context = models.TextField(blank=True, help_text="Key=value (comma separated). Keep it "
                            "simple since anything complex might be silently "
                            "dropped.")

    def __unicode__(self):
        return self.email

    @property
    def extra(self):
        """
        Parses k,v from self.extra_context and returns as dict and drops errors 
        silently.
        """
        context = {}
        for i in self.extra_context.split(','):
            # FIXME: need to explore which exceptions to catch, and which to raise
            try:
                (k, v) = i.split('=')
                context[k.strip()] = v.strip()
            except:
                pass
        return context

    @models.permalink
    def img_uri(self):
        return ('img_hits', (), {'campaign_id': self.campaign.pk,
                                 'target_id': self.pk})
    @models.permalink
    def link_uri(self):
        return ('link_hits', (), {'campaign_id': self.campaign.pk,
                                 'target_id': self.pk})

    def dispatch(self):

        if self.campaign.sender_name:
            sender = '"%s" <%s>' % (self.campaign.sender_name,
                                    self.campaign.sender_email)
        else:
            sender = self.campaign.sender_email

        context = Context(dict(target=self, campaign=self.campaign))

        text_content = Template(self.campaign.email_plain).render(context)

        if self.campaign.email_html:
            # plain text and html content
            html_content = Template(self.campaign.email_html).render(context)

            msg = EmailMultiAlternatives(self.campaign.subject, text_content,
                                         sender, [self.email])
            msg.attach_alternative(html_content, "text/html")
        else:
            # plain text only
            msg = EmailMessage(self.campaign.subject, text_content, sender,
                               [self.email])
        msg.send()

