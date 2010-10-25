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

# python
from datetime import datetime as dt

# this app
from ljsync.models import LJPost
from ljsync.protocol import LiveJournalClient
from ljsync.conf.settings import LJ_USERNAME, LJ_PASSWORD_MD5, BLOG_ENTRY_CROSSPOST_FIELD

def fix_dates(sender, instance, **kw):
    " Fix dates for a LJPost before saving it. To be called on pre_save. "
    # parse add date (from mysql/rfc)
    #   local TZ
    if not instance.pub_date:
        instance.pub_date = dt.strptime(instance.eventtime, '%Y-%m-%d %H:%M:%S')
    # parse rev date (from unixtime)
    #   UTC. Maybe use utctimestamp()?
    if instance.revtime:
        instance.rev_date = dt.fromtimestamp(int(instance.revtime))

def export(sender, instance, **kw):
    " Export given LJPost to LiveJournal. To be called on pre_save. "
    if instance.itemid: return
    # publish it to LiveJournal (remote)
    ljc = LiveJournalClient(LJ_USERNAME,  LJ_PASSWORD_MD5)
    instance.itemid = ljc.add_event(
        event    = instance.event,
        subject  = instance.subject,
        date     = instance.pub_date,
        security = instance.security,
    )

def crosspost(sender, instance, **kw):
    """ Cross-post a Post to LiveJournal and return an LJPost instance
    on success. To be called on post_save.
    """
    # TODO: IMPORTANT: add support for custom field mappings
    # TODO: render "event" to HTML and then save to LJPost as preformatted
    if not kw['created']:
        return
    if BLOG_ENTRY_CROSSPOST_FIELD:
        try:
            allowed = getattr(instance, BLOG_ENTRY_CROSSPOST_FIELD)
        except AttributeError, e:
            raise AttributeError('Wrong LJ_BLOG_ENTRY_CROSSPOST_FIELD setting: '
                                 '%s' % e.message)
        else:
            if not allowed: return
    # create local LJPost object
    ljp = LJPost(
        subject    = instance.title,
        event      = instance.body,
        pub_date   = instance.pub_date,
        eventtime  = instance.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
        security   = (instance.private and 'private' or ''),
        local_post = instance,
    )
    ljp.save()
