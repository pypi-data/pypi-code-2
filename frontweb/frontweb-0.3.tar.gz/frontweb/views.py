# -*- encoding: utf-8- -*-
import os
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import Http404
from django.core.servers.basehttp import FileWrapper
from yapsy.PluginManager import PluginManager
import rst2html
from utils import *

__all__ = ['query_file']

def query_file(request, url):
    "Gestiona la solicitud de un archivo al servidor."

    # asume que la página principal se llama index, index.rst etc...
    if not url:
        url = 'index'

    try:
        filename = get_real_filename(url)
    except IOError:
        content = "El archivo '%s' no existe" %(url)
        raise Http404


    # Si el archivo es estatico lo emite directamente
    if not is_text_file(filename):
        return send_file(request, filename)
    else:
        content = rst2html.rst2html(filename)
        navbar = rst2html.rst2html(get_real_filename("navbar"))
        footer = rst2html.rst2html(get_real_filename("footer"))
        sidebar = rst2html.rst2html(get_real_filename("sidebar"))
        title = rst2html.rst2html(get_real_filename("title"))

    template = os.path.join(obtener_directorio_templates(), "show.html")

    return render_to_response(template, {
        'content': content, 
        'navbar': navbar,
        'footer': footer,
        'sidebar': sidebar,
        'title': title,
        'head_title': get_title_from_body_html(content, filename),
        }
        )


def send_file(request, url):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.
    """
    filename = url
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response


def list_plugins(request):
    import pluginsmanager

    pm = pluginsmanager.PluginsManager()

    for plugin in pm.listar_plugins():
        print plugin.description

    nombres = [plugin.name for plugin in pm.listar_plugins()]

    if not nombres:
        content = u"No hay complementos"
    else:
        nombres_como_lista = [u"* " + nombre for nombre in nombres]
        content = rst2html.get_title_and_body(u"\n".join(nombres_como_lista))[1]

    return render_to_response("plugins.html", {
        'plugins': content,
        })
