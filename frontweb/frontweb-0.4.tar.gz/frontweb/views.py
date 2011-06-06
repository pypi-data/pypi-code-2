# -*- encoding: utf-8- -*-
import os
import mimetypes

from yapsy.PluginManager import PluginManager
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseNotFound
from django.core.servers.basehttp import FileWrapper

from frontweb import html, utils, conversor, pluginsmanager

def mostrar_archivo_o_ejecutar_plugin(request, url):
    try:
        return mostrar_archivo_convertido_en_html(request, url)
    except Http404:
        prefix = url.split('/')[0]

        plugins = obtener_plugins_como_lista()

        # Busca el plugin solicitado y si lo encuentra lo ejecuta.
        for p in plugins:
            if p.name.lower() == prefix:
                arguments_url = utils.remover_prefijo_de_url(url, prefix)
                return p.plugin_object.run(request, arguments_url)

    return HttpResponseNotFound(obtener_codigo_pagina_error(url))

def mostrar_archivo_convertido_en_html(request, url):
    "Muesta un archivo de texto rst en formato HTML."

    # asume que la página principal se llama index,
    # index.rst o index.txt
    if not url:
        url = 'index'

    try:
        filename = utils.obtener_nombre_real_del_archivo(url)
    except IOError:
        content = "El archivo '%s' no existe" %(url)
        raise Http404("No se encuentra el archivo")

    # Si el archivo es estatico lo emite directamente.
    if not utils.es_archivo_de_texto(filename):
        if os.path.isfile(filename):
            return enviar_archivo(request, filename)
        else:
            return HttpResponseNotFound(obtener_codigo_pagina_error(url))


    # Si es una archivo de texto, en cambio, lo convierte a html.
    contenido = conversor.convertir_archivo_en_html(filename)
    return utils.mostrar_pagina(contenido, filename)


def enviar_archivo(request, url):
    "Contesta la peticion enviando un archivo estatico."
    filename = url
    wrapper = FileWrapper(file(filename))
    (mimeinfo, _) = mimetypes.guess_type(filename)
    response = HttpResponse(wrapper, content_type=mimeinfo)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def obtener_plugins_como_lista():
    "Retorna una lista de todos los plugins instalados."
    return pluginsmanager.plugins_manager.listar_plugins()

def listar_plugins(request):
    plugins = obtener_plugins_como_lista()

    nombres = [plugin.name for plugin in plugins]

    if not nombres:
        content = u"No hay complementos"
    else:
        titulo = [
                "Complementos",
                "============",
                ""
                ]

        nombres_como_lista = [u"* " + nombre for nombre in nombres]
        contenido_como_rst = u"\n".join(titulo + nombres_como_lista)
        contenido_como_html = conversor.convertir_texto_en_html(contenido_como_rst)[1]

    return utils.mostrar_pagina(contenido_como_html, 'plugins')

def obtener_codigo_pagina_error(url):
    if not url:
        url = 'index.rst'
    nombre_archivo = os.path.basename(url)
    nombre_archivo = nombre_archivo.replace(".rst", "").replace(".txt", "")
    palabras = nombre_archivo.split("_")

    url_find = "/find?query=%s" %("|".join(palabras))
    titulo = "Error 404, no se encuentra el archivo"
    descripcion = "No se encuentra el archivo solicitado: <strong>%s</strong>" %(url)
    opciones = u"¿Quiere <a href='%s'>buscar páginas similares</a>?." %(url_find)

    return utils.mostrar_pagina("<h1>%s</h1><p>%s<p>%s" %(titulo, descripcion, opciones), "error 404")
