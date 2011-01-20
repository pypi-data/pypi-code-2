# -*- encoding: utf-8- -*-
import os
import subprocess
import re

HTML_TITLE_PATTERN = re.compile('<h1 class="title">(.+)</h1>')

def get_real_filename(file_path):
    """Busca el archivo solicitado y retorna la ruta al mismo, o similares.

    Si el archivo no se encuentra tal y como indica el parámetro
    ``file_path``, se insistirá buscando alguno que tenga nombre
    similar pero con extensión ``rst``, ``txt`` o similares.
    """
    alternatives = ["", ".rst", ".txt", ".TXT", ".RST"]

    for sufix in alternatives:
        if os.path.exists("data/" + file_path + sufix):
            return "data/" + file_path + sufix

    raise IOError("No se encuentra el archivo '%s'" %(file_path))

def is_text_file(path):
    """
    Indica si un archivo es de solo texto o no.
    """
    return path.endswith(".rst") or path.endswith(".txt")

def get_title_from_body_html(html_code, return_value_on_error):
    "Retorna el contenido del titulo principal de un texto HTML."
    result = HTML_TITLE_PATTERN.findall(html_code)

    if result:
        return result[0]

    return return_value_on_error

def crear_proyecto_de_django(nombre):
    from django.core.management.commands import startproject
    from django.core.management.base import CommandError

    start = startproject.Command()

    try:
        start.handle_label(nombre)
    except CommandError, e:
        raise Exception("Lo siento, no se puede crear el directorio.", e)

    print "Se ha creado el directorio '%s'." %(nombre)
    print "Ingrese en el, y luego ejecute 'frontweb run' para iniciar el servidor."

def iniciar_servidor(puerto="8000"):

    if not os.path.exists("manage.py"):
        raise Exception("Tiene que ejecutar este comando dentro del directorio proyecto.")

    subprocess.call(["python", "manage.py", "runserver", puerto])


def generar_archivo_url(nombre_del_proyecto):
    url_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_url.py")
    dst_path = os.path.join(nombre_del_proyecto, "urls.py")

    print "Generando el archivo 'url.py' de ejemplo."

    os.system("cp %s %s" %(url_file_path, dst_path))

def generar_archivo_config(nombre_de_proyecto):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_settings.py")
    dst_path = os.path.join(nombre_de_proyecto, "settings.py")

    print "Generando el archivo de configuración 'settings.py'."

    os.system("cp %s %s" %(config_file, dst_path))

def copiar_directorio_data(nombre_del_proyecto):
    dirname = obtener_directorio_data()
    os.system("cp -R %s %s" %(dirname, nombre_del_proyecto))
    print "Generando el directorio 'data'"

def obtener_directorio_templates():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

def obtener_directorio_data():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

