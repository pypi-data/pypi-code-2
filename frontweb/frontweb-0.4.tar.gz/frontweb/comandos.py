import os
import sys
import subprocess

from django.core.management.base import copy_helper, CommandError

def crear_archivo_desde_plantilla(ruta, plantilla, nombre):
    contenido = plantilla.replace("nombre", nombre).replace("Nombre", nombre.title())
    archivo = open(ruta, "wt")
    print "Creando el archivo '%s'." %(ruta)
    archivo.write(contenido)
    archivo.close()


def crear_proyecto_de_django(nombre):
    from django.core.management.commands import startproject
    from django.core.management.base import CommandError

    if os.path.exists(nombre):
        print "Lo siento, el directorio '%s' ya existe." %(nombre)
        sys.exit(-1)

    start = startproject.Command()

    try:
        start.handle_label(nombre)
    except CommandError, e:
        raise Exception("Lo siento, no se puede crear el directorio.", e)

    print "Se ha creado el directorio '%s'." %(nombre)
    print "Ingrese en el, y luego ejecute 'frontweb run' para iniciar el servidor."

    generar_archivo_url(nombre)
    copiar_directorio_data(nombre)
    modificar_configuracion_para_incluir_frontweb(nombre)

def modificar_configuracion_para_incluir_frontweb(nombre):
    "Modifica el archivo settings para indicar que usa frontweb."

    # Lee el contenido de la configuracion por defecto.
    archivo = open(os.path.join(nombre, "settings.py"), 'rt')
    settings = archivo.read()
    archivo.close()

    # Agrega 'frontweb' a la lista de aplicaciones instaladas.
    settings = settings.replace("INSTALLED_APPS = (\n", "INSTALLED_APPS = (\n'frontweb',\n")

    # Guarda el archivo modificado.
    archivo = open(os.path.join(nombre, "settings.py"), 'wt')
    archivo.write(settings)
    archivo.close()



def iniciar_servidor(host=None, puerto=None):
    if not os.path.exists("manage.py"):
        print "Tiene que usar este comando dentro del directorio proyecto frontweb."
        sys.exit(-1)

    if not host:
        host = "0.0.0.0"

    if not puerto:
        puerto = '8000'

    escucha = "%s:%s" %(host, puerto)
    subprocess.call(["python", "manage.py", "runserver", escucha])

def generar_archivo_url(nombre_del_proyecto):
    url_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_url.py")
    dst_path = os.path.join(nombre_del_proyecto, "urls.py")

    print "Generando el archivo 'url.py' de ejemplo."

    os.system("cp '%s' '%s'" %(url_file_path, dst_path))

def copiar_directorio_data(nombre_del_proyecto):
    dirname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.system("cp -R '%s' '%s'" %(dirname, nombre_del_proyecto))
    print "Generando el directorio 'data'"

def crear_plugin_desde_plantillas(nombre, dir_path, plantilla_py, plantilla_descripcion):
    if not os.path.exists(dir_path):
        raise CommandError("Lo siento, el directorio 'plugins' no existe.")

    archivo_py = os.path.join(dir_path, nombre + '.py')
    archivo_descripcion = os.path.join(dir_path, nombre +'.yapsy-plugin')

    if os.path.exists(archivo_py):
        raise CommandError("Lo siento, ya existe un plugin con ese nombre...")

    crear_archivo_desde_plantilla(archivo_py, plantilla_py, nombre)
    crear_archivo_desde_plantilla(archivo_descripcion, plantilla_descripcion, nombre)

def crear_plugin(nombre, dir_path):
    plantilla_py = """from yapsy.IPlugin import IPlugin
from frontweb import utils

class Nombre(IPlugin):
    name = "nombre"

    def run(self, request, url):
        return utils.mostrar_pagina("Este plugin no esta implementado", "nombre")
"""
    plantilla_descripcion = """[Core]
Name = Nombre
Module = nombre

[Documentation]
Author = sin definir
Version = 0.1
Website = http://www.frontweb.com.ar
Description = Sin definir
"""
    crear_plugin_desde_plantillas(nombre, dir_path, plantilla_py, plantilla_descripcion)

def crear_directiva(nombre, dir_path):
    plantilla_py = """from yapsy.IPlugin import IPlugin
from docutils import nodes
from docutils.parsers.rst import directives, Directive

from frontweb import utils

class DirectivaNombre(IPlugin):
    name = "nombre"

    def run(self, request, url):
        return utils.mostrar_pagina("Esta la pagina de la directiva nombre", "nombre")

class NombreDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()
        text = '<div>Contenido de la directiva nombre: <pre>%s</pre></div>' % self.content
        return [nodes.raw('', text, format='html')]

directives.register_directive("nombre", NombreDirective)
"""
    plantilla_descripcion = """[Core]
Name = DirectivaNombre
Module = nombre

[Documentation]
Author = sin definir
Version = 0.1
Website = http://www.frontweb.com.ar
Description = Sin definir
"""
    crear_plugin_desde_plantillas(nombre, dir_path, plantilla_py, plantilla_descripcion)
