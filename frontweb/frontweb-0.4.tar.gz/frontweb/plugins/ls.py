import os
from yapsy.IPlugin import IPlugin
from django.http import HttpResponseNotFound

from frontweb import settings, utils

DATA = settings.FRONTWEB_DATA

class Ls(IPlugin):
    name = "ls"

    def run(self, request, url):
        parametro_get = request.GET.get('dir', None)

        if parametro_get:
            expresion = parametro_get
        else:
            expresion = url

        # Agregamos una barra al final de la expresion solo si la exprexion no
        # es vacia.
        if len(url) > 1 and not url.endswith("/"):
            expresion = expresion + "/"

        raiz = os.path.abspath(os.path.join(DATA, expresion))

        # Solo queremos listar archivos desde DATA hacia adentro.
        if not utils.path_dentro_de_raiz(raiz, DATA):
            raiz = os.path.abspath(DATA)

        try:
            directorios, archivos = self.get_file_list(raiz)
        except OSError:
            return HttpResponseNotFound("No se encuentra la ruta solicitada, o no es un directorio: %s" %(url))

        resultado = self._convertir_directorio_a_html(url, directorios, archivos)
        return utils.mostrar_pagina("<h1>Resultado de busqueda para: %s</h1> %s" %(expresion, resultado), 'ls')

    def _convertir_directorio_a_html(self, url, directorios, archivos):

        html = '<ul class="ls">'

        if not url:
            pass
        else:
            html += '<li><a href="../"><img src="/icons/folder.png">..</a></li>'

        if directorios:
          for d in directorios:
            html += '<li><a href="/ls/%s%s/"><img src="/icons/folder.png">%s</a></li>' % (url, d, d)

        if archivos:
          for a in archivos:
            html += '<li><a href="/%s%s"><img src="/icons/txt.png"> %s</a></li>' % (url, a, a)

        html += '</ul>'
        return html

    def get_file_list(self, directory):
        "Retorna una lista de objetos que representan archivos y directorios."

        all_entries = os.listdir(directory)

        # filtra la lista de archivos en dos grupos
        files = [x for x in all_entries if os.path.isfile(directory + '/' + x)]
        directories = [x for x in all_entries if os.path.isdir(directory + '/' + x) and not x.startswith(".")]

        return (directories, files)
