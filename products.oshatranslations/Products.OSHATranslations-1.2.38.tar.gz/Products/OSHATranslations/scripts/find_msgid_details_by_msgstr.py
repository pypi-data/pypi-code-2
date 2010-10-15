#!/usr/bin/env python

import poutils

osha_i18n = "/home/cillian/Syslab/OSHA/src/Products.OSHATranslations/Products/OSHATranslations/i18n"
plone_i18n = "/home/cillian/Syslab/OSHA/parts/omelette/plone/app/locales/i18n"
ignored_langs = ["ru", "no", "tr", "ja"]

all_msgstrs = [
    "Edit this page",
    "Manage News",
    "Manage Events",
    "Risk assessment tools",
    "Useful links",
    "Case studies",
    "Providers"
    "Authorities", 
    "Social Partners",
    "Research Organisations", 
    "Other National Sites", 
    "More Related Content",
    ]

all_msgstrs = ["Database"]

all_msgstrs = [
 "Edit this page",
 "Manage News",
 "label_manage_events",
]

all_msgstrs = ["Category", "category", "categories"]

osha_po = poutils.PoDirectory(osha_i18n, ignored_langs)
plone_po = poutils.PoDirectory(plone_i18n, ignored_langs)


osha_unt = osha_po.find_all_untranslated(all_msgstrs)
plone_unt = plone_po.find_all_untranslated(all_msgstrs)
print osha_unt
print plone_unt
import pdb; pdb.set_trace()
