# -*- coding: utf-8 -*-
from docutils import core, io
import os
import re

HTML_TITLE_PATTERN = re.compile('<h1 class="title">(.+)</h1>')

def obtener_partes(input_string, source_path=None, 
        destination_path=None, input_encoding='unicode', 
        doctitle=1, initial_header_level=1):
    """
    Obtiene un diccionario de elementos HTML de una cadena HTML.

    Parametros:

    - input_string: la cadena de texto.
    - source_path: la ruta al archivo que se esta procesando.
    - destination_path: ruta destino del archivo generado.
    - input_encoding: tipo de cadena (usa unicode).
    - doctitle: titulo del documento como primer cadena.
    - initial_header_level: el nivel inicial para cabeceras, 1 es h1.

    """
    overrides = {'input_encoding': input_encoding,
                 'doctitle_xform': doctitle,
                 'initial_header_level': initial_header_level}
    parts = core.publish_parts(
        source=input_string, source_path=source_path,
        destination_path=destination_path,
        writer_name='html', settings_overrides=overrides)

    return parts


def obtener_titulo_principal_del_cuerpo(html_code, return_value_on_error):
    "Retorna el contenido del titulo principal de un texto HTML."
    result = HTML_TITLE_PATTERN.findall(html_code)

    if result:
        return result[0]

    return return_value_on_error
