# -*- encoding: utf-8 -*-

import os
import sys

from django.utils import unittest

sys.path.append(os.path.abspath(".."))

import utils
import conversor
import html
from frontweb import settings

DATA = settings.FRONTWEB_DATA

# Contenido que se espera generar en HTML
# luego de tomar un fixture y procesarlo.
TXT = '<div class="document" id="hola">\n<h1 class="title">Hola</h1>\n<p>mundo</p>\n</div>\n'
SAMPLE_RST = u"""
Hola
====

mundo
"""


class TestRestructuredText(unittest.TestCase):
    "Pruebas sobre el motor de conversion rst a html."

    def testConversor(self):
        path = os.path.join(DATA, "fixtures", "fixture.rst")
        html_content = conversor.convertir_archivo_en_html(path)
        self.assertEquals(html_content, TXT)

    def testTituloYCuerpo(self):
        title, body = conversor.convertir_texto_en_html(SAMPLE_RST)

        self.assertEquals(title, "Hola")
        self.assertEquals(body, TXT)

    def testPartesDeUnHTML(self):
        parts = html.obtener_partes(u"<H1>HOLA</H1>")

        self.assertTrue('footer' in parts.keys())
        self.assertTrue('title' in parts.keys())
        self.assertTrue('meta' in parts.keys())
        self.assertTrue('body' in parts.keys())
        self.assertTrue('encoding' in parts.keys())



class TestUtils(unittest.TestCase):
    "Pruebas sobre las utilidades de frontweb."

    def testNombreReal(self):
        path = os.path.join(DATA, "fixture.rst")
        self.assertEquals(utils.obtener_nombre_real_del_archivo("fixture"), path)

    def testArchivoInexistente(self):
        self.assertRaises(IOError, self.solicitar_archivo_que_no_existe)

    def solicitar_archivo_que_no_existe(self):
        utils.obtener_nombre_real_del_archivo("archivo_que_no_existe.txt")

    def testTiposDeArchivos(self):
        self.assertTrue(utils.es_archivo_de_texto("hola.rst"))
        self.assertTrue(utils.es_archivo_de_texto("hola.txt"))
        self.assertFalse(utils.es_archivo_de_texto("hola.jpg"))

    def testFechas(self):
        self.assertTrue(utils.es_un_nombre_con_fecha("2010-10-10texto"))
        self.assertTrue(utils.es_un_nombre_con_fecha("Mi texto del 2010-10-10"))
        self.assertFalse(utils.es_un_nombre_con_fecha("Mi texto de..."))

    def testExtraerFechas(self):
        fecha = utils.obtener_fecha_del_archivo("2010-10-03-texto.rst")
        self.assertEquals(fecha.year, 2010)
        self.assertEquals(fecha.month, 10)
        self.assertEquals(fecha.day, 03)

        fecha = utils.obtener_fecha_del_archivo('2011-10-10_el_mas_nuevo_de_todos.rst')
        self.assertEquals(fecha.year, 2011)
        self.assertEquals(fecha.month, 10)
        self.assertEquals(fecha.day, 10)

        fecha = utils.obtener_fecha_del_archivo('2011-09-10_casi_el_mas_nuevo.rst')
        self.assertEquals(fecha.year, 2011)
        self.assertEquals(fecha.month, 9)
        self.assertEquals(fecha.day, 10)

        fecha = utils.obtener_fecha_del_archivo('2010-10-03_dia_3.rst')
        self.assertEquals(fecha.year, 2010)
        self.assertEquals(fecha.month, 10)
        self.assertEquals(fecha.day, 03)

    def testOrdenarFechas(self):
        lista_de_archivos = ['2010-01-01_archivo_muy_viejo.rst',
                             '2010-02-01_casi_ultimo.rst',
                              '2011-10-10_el_mas_nuevo_de_todos.rst',
                              '2011-09-10_casi_el_mas_nuevo.rst',
                              '2010-10-03_dia_3.rst',
                              '2010-10-05_dia_5.rst',
                              '2010-10-01_dia_1.rst']

        lista_de_archivos.sort(cmp=utils.comparar_dos_fechas_para_ordenar)
        self.assertEquals(lista_de_archivos[0], '2011-10-10_el_mas_nuevo_de_todos.rst')
        self.assertEquals(lista_de_archivos[1], '2011-09-10_casi_el_mas_nuevo.rst')
        self.assertEquals(lista_de_archivos[2], '2010-10-05_dia_5.rst')
        self.assertEquals(lista_de_archivos[3], '2010-10-03_dia_3.rst')
        self.assertEquals(lista_de_archivos[4], '2010-10-01_dia_1.rst')
        self.assertEquals(lista_de_archivos[5], '2010-02-01_casi_ultimo.rst')
        self.assertEquals(lista_de_archivos[6], '2010-01-01_archivo_muy_viejo.rst')


    def testObtenerArchivosConFechas(self):
        archivos_con_fechas = utils.obtener_todos_los_archivos_de_texto_con_fecha(DATA)

    def testRemoverPrefijoDeUrl(self):
        self.assertEquals(utils.remover_prefijo_de_url("ls/asdls/asd", "ls"), "asdls/asd")
        self.assertEquals(utils.remover_prefijo_de_url("ls", "ls"), "")
        self.assertEquals(utils.remover_prefijo_de_url("ls/", "ls"), "")
        self.assertEquals(utils.remover_prefijo_de_url("ls/ls", "ls"), "ls")
        self.assertEquals(utils.remover_prefijo_de_url("ls/ls/", "ls"), "ls/")
        self.assertEquals(utils.remover_prefijo_de_url("ls/ls/", "ls"), "ls/")
        self.assertRaises(ValueError, utils.remover_prefijo_de_url, "ls/ls/", "feed")

    def testPathDentroDeRaiz(self):
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar", "/foo"))
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar", "/foo/bar"))
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar/", "/foo/bar"))
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar/else", "/foo/bar"))
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar/else", "/foo/bar"))
        self.assertTrue(utils.path_dentro_de_raiz("/foo/bar/../", "/foo"))
        self.assertTrue(utils.path_dentro_de_raiz("foo/bar/../", "foo/"))
        self.assertFalse(utils.path_dentro_de_raiz("/bar/foo", "/foo"))
        self.assertFalse(utils.path_dentro_de_raiz("/foo/bar/../../", "/foo"))
        self.assertFalse(utils.path_dentro_de_raiz("foo/bar/../../", "foo"))
        self.assertFalse(utils.path_dentro_de_raiz("/foo", "foo"))


class TestPlugins(unittest.TestCase):
    "Pruebas al sistema de complementos."

    def testImportarYapsy(self):
        import yapsy


class TestConfiguracion(unittest.TestCase):

    def testConfiguracion(self):
        import frontweb

        nombre = frontweb.configuracion.obtener('general', "nombre", None)
        self.assertTrue(nombre, "El sitio tiene algun nombre")


if __name__ == '__main__':
    unittest.main()
