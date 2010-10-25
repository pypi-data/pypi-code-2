# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009 Andy Mikhailenko and contributors
#
#  This file is part of Django LJSync.
#
#  Django LJSync is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

# django
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import (BooleanField, CharField, DateTimeField, IntegerField,
                              ForeignKey, Model, PositiveIntegerField, TextField,
                              URLField)
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _

# apps
from autoslug.fields import AutoSlugField

# this app
from ljsync.conf.settings import BLOG_ENTRY_MODEL

post_model = None
if BLOG_ENTRY_MODEL:
    app_label, model = BLOG_ENTRY_MODEL.split('.')
    try:
        entry_model = getattr(__import__('%s.models' % app_label, globals(), {}, ['']), model)
    except AttributeError, e:
        raise AttributeError, 'Wrong LJ_BLOG_ENTRY_MODEL setting: %s' % e.message

class LJPost(Model):
    " A cached LiveJournal post. "
    security_choices = (
        (None,      'Public'),
        ('private', 'Private'),
        ('usemask', 'Fine-grained'),
    )
    subject   = CharField("Subject", max_length=250)
    event     = TextField("Body")
    eventtime = CharField("Date and time (raw)", max_length=50)
    pub_date  = DateTimeField("Date and time", max_length=50, blank=True, null=True)
    revtime   = IntegerField("Last updated (raw)", blank=True, null=True)
    rev_date  = DateTimeField("Last updated", blank=True, null=True)
    revnum    = IntegerField("Number of revisions", default=0,
                             help_text='Number of times this post was edited')
    # how to locate the post in original system:
    url       = URLField(blank=True, null=True)
    itemid    = IntegerField(unique=True)
    # categorization
    taglist   = CharField('Tags', max_length=250, blank=True, null=True,
                          help_text="Comma-separated list of tags")
    # parsing mode
    opt_preformatted = BooleanField(default=False)
    # more
    current_location = CharField("Location", max_length=250, blank=True, null=True)
    current_music    = CharField("Music", max_length=250, blank=True, null=True)
    current_moodid   = IntegerField("Mood ID (if known)", blank=True, null=True)
    current_mood     = CharField("Mood", max_length=250, blank=True, null=True)
    # security
    security  = CharField("Security", choices=security_choices, max_length=8,
                          blank=True, null=True)
    allowmask = IntegerField("ACL", blank=True, null=True,
                             help_text="If security is 'usemask' then this is "
                                       "defined with the 32-bit unsig int bitmask"
                                       "of who is allowed to access this post.")

    # Post field
    content_type = ForeignKey(ContentType, null=True, blank=True,
                              related_name="lj_post_for_%(class)s")
    object_id    = PositiveIntegerField(null=True, blank=True)
    local_post   = GenericForeignKey()

    __unicode__ = lambda self: self.subject or u'#%s: %s' % (self.itemid,
                                                             self.pub_date)

    # for admin
    def get_local_post(self):
        "Returns corresponding local post (custom model)."
        return '<a href="%s">%s</a>' % (self.local_post.get_absolute_url(),
                                        self.local_post)
    get_local_post.short_description = 'Corresponding local post'
    get_local_post.allow_tags = True

    class Meta:
        ordering = ['-pub_date']

# REGISTER SIGNALS

from ljsync.signals import fix_dates, export, crosspost

pre_save.connect(fix_dates, sender=LJPost)
pre_save.connect(export, sender=LJPost)
# allow crossposting if a model is specified:
if BLOG_ENTRY_MODEL:
    post_save.connect(crosspost, sender=entry_model)
