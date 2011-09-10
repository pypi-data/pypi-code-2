# -*- coding: utf-8 -*-
"""
Frontweb is a frontend of restructuredtext for create blog and wiki pages.

License (GPL), see LICENSE file for more details.
Copyright 2010 Hugo Ruscitti <hugoruscitti@gmail.com>
"""
import codecs
from docutils import core, io
import os
import directives
import html

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass




def convertir_archivo_en_html(ruta_al_archivo_rst):
    """Convierte un archivo .rst a texto HTML.

    El retorno de esta funcion son dos cadenas, una
    con el titulo del documento y la otra con el
    contenido de la pagina html.
    """

    f = codecs.open(ruta_al_archivo_rst, "r", "utf-8" )
    content = f.read()
    f.close()

    return convertir_texto_en_html(content, ruta_al_archivo_rst)[1]



def convertir_texto_en_html(input_string, source_path=None, 
        destination_path=None, input_encoding='unicode', 
        output_encoding='unicode', doctitle=1, 
        initial_header_level=1):
    """
    Given an input string, returns an HTML fragment as a string.

    The return value is the contents of the <body> element.

    Parameters (see `html_parts()` for the remainder):

    - `output_encoding`: The desired encoding of the output.  If a Unicode
      string is desired, use the default value of "unicode" .
    """
    parts = html.obtener_partes(
        input_string=input_string, source_path=source_path,
        destination_path=destination_path,
        input_encoding=input_encoding, doctitle=doctitle,
        initial_header_level=initial_header_level)
    fragment = parts['html_body']

    title = parts['title']

    if output_encoding != 'unicode':
        fragment = fragment.encode(output_encoding)

    return title, fragment
