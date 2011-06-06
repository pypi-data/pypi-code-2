import os
from yapsy.IPlugin import IPlugin
from django.http import Http404, HttpResponseForbidden

from frontweb import settings, utils

DATA = settings.FRONTWEB_DATA

class Raw(IPlugin):
    name = "raw"

    def run(self, request, url):
        if url:
            nombre = url
            mensaje = ''

            if not utils.path_dentro_de_raiz(os.path.join(DATA, nombre), DATA):
                return HttpResponseForbidden("Prohibido: %s" % nombre)

            try:
                filename = utils.obtener_nombre_real_del_archivo(nombre)
            except IOError:
                return utils.mostrar_pagina("El archivo solicitado no se puede abrir: %s" %(nombre), "error");

            if utils.es_archivo_de_texto(filename):
                archivo = open(filename, 'rt')
                mensaje = archivo.read()
                archivo.close()
            else:
                mensaje = "Solo puede usar la directiva raw con archivos de texto."

            return utils.mostrar_pagina("<PRE>%s</PRE>" %(mensaje), "Hola")
        else:
            return utils.mostrar_pagina("Tiene que indicar un archivo a ver en la URL.", "error");
