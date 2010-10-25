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

from django.contrib import admin
from models import LJPost

class LJPostAdmin(admin.ModelAdmin):
    list_display       = ('itemid', 'pub_date', 'subject', 'security',
                          'allowmask', 'url', 'get_local_post')
    list_display_links = ('itemid', 'pub_date', 'subject')
    list_filter        = ('security', 'allowmask', 'opt_preformatted')
    date_hierarchy     = 'pub_date'
    search_fields      = ('subject', 'taglist', 'event')

admin.site.register(LJPost, LJPostAdmin)
