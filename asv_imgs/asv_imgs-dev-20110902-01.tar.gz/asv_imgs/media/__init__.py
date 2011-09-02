# -*- coding: utf-8 -*-
from __future__ import unicode_literals
    
#from django.utils.functional import lazy
#from django.core.urlresolvers import reverse
from asv_imgs import settings as AIS
from asv_utils.dj import reverse_lazy
#---------------------------------------------------------------
#---------------------------------------------------------------
asv_imgs__media_jQuery = AIS.ASV_IMGS_MEDIA_JQUERY_LOCATION
asv_imgs__media_jQueryUI = AIS.ASV_IMGS_MEDIA_JQUERYUI_LOCATION
asv_imgs__media_jQueryUI_css = AIS.ASV_IMGS_MEDIA_JQUERYUI_CSS_LOCATION
asv_imgs__media_jQueryCookie = reverse_lazy('asv_imgs__media', args=['js/jquery.cookie.min.js'])
asv_imgs__media_jQueryJson = reverse_lazy('asv_imgs__media', args=['js/jquery.json.min.js'])
asv_imgs__media_admin_inlines2tabs_js = reverse_lazy('asv_imgs__media', args=['js/asv_imgs__admin__inlines_to_tabs.min.js'])
asv_imgs__media_admin_sortable_js = reverse_lazy('asv_imgs__media', args=['js/asv_imgs__admin__sortable.min.js'])
asv_imgs__media_additional_css = reverse_lazy('asv_imgs__media', args=['css/asv_imgs.css'])
#---------------------------------------------------------------
#---------------------------------------------------------------
