from django.conf import settings

STAGING_REPO_DIR = getattr(settings, 'STAGING_REPO_DIR', '')
STAGING_AUTOCREATE_REPO = getattr(settings, 'STAGING_AUTOCREATE_REPO', True)

STAGING_BACKEND_CLASSES = getattr(settings, 'STAGING_BACKEND_CLASSES', [
    'staging.backends.static.StaticStagingBackend',
    'staging.backends.content.ContentStagingBackend',
    'staging.backends.templates.TemplateStagingBackend',
])

STAGING_HG_SERVE_PORT = getattr(settings, 'STAGING_HG_SERVE_PORT', '8888')

# Syntax: ( ('app1', 'Model1'), ('app2', 'Model2'), )
STAGING_MODELS_TO_SAVE = getattr(settings, 'STAGING_MODELS_TO_SAVE', [])
