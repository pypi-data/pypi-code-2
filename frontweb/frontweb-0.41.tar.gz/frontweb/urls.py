from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r"^plugins", 'frontweb.views.listar_plugins'),
    (r"^(.*)$", 'frontweb.views.mostrar_archivo_o_ejecutar_plugin'),
    # Descomentar y comentar la anterior para deshabilitar todos los plugins:
    # ("^(.*)$", 'frontweb.views.query_file'),
)
