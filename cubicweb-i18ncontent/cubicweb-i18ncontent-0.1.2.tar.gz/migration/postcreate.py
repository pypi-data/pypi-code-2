# postcreate script

for code, name in ((u'en', _('English')), (u'fr', _('French'))):
    add_entity('Language', code=code, name=name)


