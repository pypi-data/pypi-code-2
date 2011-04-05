from django.conf import settings
from webutils.helpers import grab_from_import

def import_setting_name(setting_name, default_obj=None):
    ''' Used to import an item from a value in the current 
        Django projects settings.py
        
        Example in settings.py:
        
            FORM_TO_IMPORT = 'myproject.myapp.forms.CustomForm'
        
        Then to grab this, just call import_setting_name:
        
            form = import_setting_name('FORM_TO_IMPORT')
        
        Pass 'default_obj' 
    '''
    if hasattr(settings, setting_name):
        try:
            return grab_from_import(
                getattr(settings, setting_name),
                as_from=True,
            )
        except ImportError, err:
            if default_obj is None:
                raise ImportError(str(err))
    return default_obj