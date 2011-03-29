from django.conf import settings

if 'bookreader' in settings.INSTALLED_APPS:
    if not hasattr(settings,'BOOKREADER_SIGNALS_ENABLED'):
        settings.BOOKREADER_SIGNALS_ENABLED = True
    
    if not hasattr(settings,'BOOKREADER_COMPARISON_SESSION_KEY'):
        settings.BOOKREADER_COMPARISON_SESSION_KEY = 'bookreader.compare'
    
    if not hasattr(settings,'BOOKREADER_COMPARISON_GET_ARGUMENT'):
        settings.BOOKREADER_COMPARISON_GET_ARGUMENT = 'compare'
    
    if not hasattr(settings, 'BOOKREADER_COMPARISON_TEMPLATE_VARIABLE'):
        settings.BOOKREADER_COMPARISON_TEMPLATE_VARIABLE = 'compare'
    
    if not hasattr(settings,'DJATOKA_BASE_URL'):
        raise Exception('DJATOKA_BASE_URL is a required settings')
    
    if not hasattr(settings,'DJATOKA_ARGUMENTS'):
        settings.DJATOKA_ARGUMENTS = {
            'url_ver':'Z39.88-2004',
            'svc_id':'info:lanl-repo/svc/getRegion',
            'svc_val_fmt':'info:ofi/fmt:kev:mtx:jpeg2000',
            'svc.format':'image/jpeg',
            'svc.scale':'150'}
    
    assert isinstance(settings.DJATOKA_ARGUMENTS, dict), u'DJATOKA_ARGUMENTS must be a dictionary'