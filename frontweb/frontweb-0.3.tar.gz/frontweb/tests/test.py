# -*- encoding: utf-8 -*-
import unittest
import frontweb

# Contenido que se espera generar en HTML
# luego de tomar un fixture y procesarlo.
TXT = '<div class="document" id="hola">\n<h1 class="title">Hola</h1>\n<p>mundo</p>\n</div>\n'
SAMPLE_RST = u"""
Hola
====

mundo
"""


class TestRestructuredText(unittest.TestCase):

    def setUp(self):
        pass

    def testMundo(self):
        html_content = frontweb.rst2html.rst2html('fixture.rst')
        self.assertEquals(html_content, TXT)

    def testTitleBody(self):
        title, body = frontweb.rst2html.get_title_and_body(SAMPLE_RST)

        self.assertEquals(title, "Hola")
        self.assertEquals(body, TXT)
    
    def testHTMLParts(self):
        parts = frontweb.rst2html.html_parts(u"<H1>HOLA</H1>")

        self.assertTrue('footer' in parts.keys())
        self.assertTrue('title' in parts.keys())
        self.assertTrue('meta' in parts.keys())
        self.assertTrue('body' in parts.keys())
        self.assertTrue('encoding' in parts.keys())


    def testTiposDeArchivos(self):
        self.assertTrue(frontweb.utils.is_text_file("hola.rst"))
        self.assertTrue(frontweb.utils.is_text_file("hola.txt"))
        self.assertFalse(frontweb.utils.is_text_file("hola.jpg"))

    def testArchivoInexistente(self):
        self.assertRaises(IOError, self.solicitar_archivo_que_no_existe)

    def solicitar_archivo_que_no_existe(self):
        frontweb.utils.get_real_filename("archivo_que_no_existe.txt")

    def testImportarYapsy(self):
        import yapsy
        

if __name__ == '__main__':
    unittest.main()
