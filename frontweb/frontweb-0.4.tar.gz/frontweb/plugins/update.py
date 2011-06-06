import os
from yapsy.IPlugin import IPlugin

from frontweb import settings, utils

DATA = settings.FRONTWEB_DATA

class Update(IPlugin):
    name = "update"

    def __init__(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def run(self, request, url):
        if os.path.exists(os.path.join(DATA,".hg")):
            resultado = "<h2>Pull:</h2>"
            resultado += utils.ejecutar_comando(["hg", "pull"])
            resultado += "<h2>Update:</h2>"
            resultado += utils.ejecutar_comando(["hg", "update"])
            repositorio = "Mercurial"
        elif os.path.exists(os.path.join(DATA,".git")):
            resultado = "<h2>Pull:</h2>"
            resultado += utils.ejecutar_comando(["git", "pull"])
            repositorio = "Git"
        else:
            return utils.mostrar_pagina("<h1>Error:</h1>El directorio data no esta bajo control de versiones.", 'error')

        return utils.mostrar_pagina("Actualizacion desde repositorio %s:<PRE>%s</PRE>" %(repositorio, resultado), 'update')
