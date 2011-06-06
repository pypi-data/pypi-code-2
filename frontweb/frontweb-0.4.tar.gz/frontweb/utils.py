# -*- encoding: utf-8- -*-
import os
import subprocess
import re
import datetime
import time

from django.template import loader

from frontweb import settings

DATA = settings.FRONTWEB_DATA

# Permite fechas de la forma "2010-10-10", "20101010" y "2010_10_10".
DATED_FILE = re.compile('.*(\d{4}-\d{2}-\d{2}).*')

def mostrar_pagina(cuerpo_html, nombre_archivo):
    from django.shortcuts import render_to_response
    import conversor
    import html

    generar_html = conversor.convertir_archivo_en_html
    ruta_completa = obtener_nombre_real_del_archivo


    try:
        navbar = generar_html(ruta_completa("navbar"))
        footer = generar_html(ruta_completa("footer"))
        sidebar = generar_html(ruta_completa("sidebar"))
        title = generar_html(ruta_completa("title"))
    except IOError:
        error = "No se encuentra el archivo <b>data/%s.rst</b>"
        sidebar =  error % 'sidebar'
        footer = error % 'footer'
        title = error % 'title'
        navbar = error % 'navbar'

    return render_to_response("frontweb/show.html", {
    'content': cuerpo_html,
    'navbar': navbar,
    'footer': footer,
    'sidebar': sidebar,
    'title': title,
    'head_title': html.obtener_titulo_principal_del_cuerpo(cuerpo_html, nombre_archivo),
    })


def mostrar_mensaje(titulo, mensaje):
    from django.shortcuts import render_to_response
    template = os.path.join(obtener_directorio_templates(), "message.html")
    return render_to_response(template, {
            'title_1': titulo,
            'message': mensaje,
            }
    )

def obtener_nombre_real_del_archivo(original_file_path):
    """Busca el archivo solicitado y retorna la ruta al mismo, o similares.

    Si el archivo no se encuentra tal y como indica el parámetro
    ``file_path``, se insistirá buscando alguno que tenga nombre
    similar pero con extensión ``rst``, ``txt`` o similares.
    """
    alternatives = ["", ".rst", ".txt", ".TXT", ".RST"]

    for sufix in alternatives:
        file_path = os.path.join(DATA, original_file_path + sufix)
        if os.path.exists(file_path):
            if not os.path.isdir(file_path):
                return file_path

    raise IOError("No se encuentra el archivo '%s'" %(original_file_path))

def es_archivo_de_texto(path):
    """
    Indica si un archivo es de solo texto o no.
    """
    return path.endswith(".rst") or path.endswith(".txt")

def obtener_todos_los_archivos_de_texto(path):
    "Retorna una lista con todos los archivos de texto en el directorio indicado."
    l = []

    def collect(arg, dirname, fnames):
        for fn in fnames:
            if fn.endswith('.rst') or fn.endswith('.txt'):
                l.append(os.path.join(dirname, fn))

    if not path.startswith("."):
        os.path.walk(path, collect, None)

    return l

def obtener_todos_los_archivos_de_texto_con_fecha(path):
    """Retorna una lista de los archivos que tienen una fecha en su nombre.

    Esta lista se retorna en base a una ruta, y la
    lista llegará ordenada de la fecha mas reciente a
    las mas antigua.
    """
    todos_los_archivos = obtener_todos_los_archivos_de_texto(path)
    lista = [x for x in todos_los_archivos if es_un_nombre_con_fecha(x)]
    lista.sort(cmp=comparar_dos_fechas_para_ordenar)
    return lista

def es_un_nombre_con_fecha(path):
    "Indica si un archivo tiene una fecha en el nombre de archivo."
    if DATED_FILE.match(path):
        return True


def obtener_fecha_del_archivo(filename):
    "Retorna un objeto Date desde el nombre de un archivo con fecha."
    date_as_string = DATED_FILE.match(filename).group(1)

    def obtener_objeto_date_desde_cadena(string):
        "Genera un objeto Datetime desde una cadena."
        c = datetime.datetime.strptime(string,"%Y-%m-%d")
        return c.replace(hour=0, minute=0, second=0)

    return obtener_objeto_date_desde_cadena(date_as_string)

def comparar_dos_fechas_para_ordenar(f1, f2):
    "Indica el orden de dos fechas para ordenar listas de archivos."
    d1 = obtener_fecha_del_archivo(f1)
    d2 = obtener_fecha_del_archivo(f2)

    if d1 < d2:
        return 1
    else:
        return -1

def ejecutar_comando(lista_de_comandos, cwd=DATA):
    "Ejecuta un comando y retorna la salida en formato cadena."

    #print "utils.py: ejecutando el comando", lista_de_comandos[0]

    process = subprocess.Popen(lista_de_comandos,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               cwd=cwd)
    return process.communicate()[0]


def filtrar_lista_por_expresion_regular(expresion, lista):
    "Retorna una lista reducida de todos los elementos de complen la expresion."
    exp = re.compile(expresion)
    return filter(exp.search, lista)

def remover_prefijo_de_url(url, prefijo):
    """Quita el prefijo de la url. Si la url no comienza con el prefijo levanta
    ValueError.
    """
    if not url.startswith(prefijo):
        raise ValueError("La url no comienza con el prefijo")
    url = url[len(prefijo):]
    if url.startswith("/"):
        url = url[1:]
    return url

def path_dentro_de_raiz(path, raiz):
    """Devuelve verdadero cuando el path está dentro del árbol de la raiz.
    Ej: path_dentro_de_raiz("/foo/bar", "/foo") -> True
        path_dentro_de_raiz("/bar/foo", "/foo") -> False
        path_dentro_de_raiz("foo/bar", "foo/bar/else") -> True
    """
    abs_raiz, abs_path = os.path.abspath(raiz), os.path.abspath(path)
    common = os.path.commonprefix((abs_raiz, abs_path))
    return common.startswith(abs_raiz)
