# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpRequest, QueryDict
from django.utils.encoding import smart_str

from models import Author, Whatamess, Book

from latex import LatexDocument

from os.path import join
from cStringIO import StringIO
import re

class SimpleTestCase(TestCase):
    """Tests with django Forum
    """
    def setUp(self):
        """
        """
        self.auth1 = Author.objects.create(name="Raymond E Feist")
        self.book1 = Book.objects.create(author=self.auth1, title="Daughter of the Empire")

    def testLatexDocument(self):
        """Test Latex document parsing
        """
        simple_report = open(join(settings.MEDIA_ROOT, 'report.tex',), 'r').read()
        ltxdoc = LatexDocument(simple_report)
        self.assertTrue(isinstance(ltxdoc, LatexDocument))

        # documentclass Test
        self.assertEqual(ltxdoc.document_class, "report")
        self.assertEqual(len(ltxdoc.document_class_opts), 2)
        self.assertEqual(ltxdoc.document_class_opts[1], "11pt")

        # Packages test
        self.assertEqual(len(ltxdoc.packages), 8)

        # Preamble test
        self.assertTrue("My title" in ltxdoc.preamble)
        self.assertFalse("ABSTRACT" in ltxdoc.preamble)
        self.assertFalse("usepackage" in ltxdoc.preamble)
        self.assertFalse("documentclass" in ltxdoc.preamble)

        # Document test
        self.assertFalse("My title" in ltxdoc.document)
        self.assertFalse("usepackage" in ltxdoc.document)
        self.assertFalse("documentclass" in ltxdoc.document)
        self.assertTrue("ABSTRACT" in ltxdoc.document)

    def testLatexDocumentPrint(self):
        """Test Latex document parsing
        """
        simple_report = open(join(settings.MEDIA_ROOT, 'report.tex',), 'r').read()
        ltxdoc = LatexDocument(simple_report)
        ltxresult = str(ltxdoc)

        # documentclass Test
        self.assertTrue("\documentclass[a4paper,11pt]{report}" in ltxresult)

        # Packages test
        self.assertTrue("\usepackage[pdftex=true, hyperindex=true, colorlinks=true]{hyperref}" in ltxresult)

        # Preamble test
        self.assertTrue("\date{ tomorrow }" in ltxresult)

        # Document test
        self.assertTrue("\\begin{document}" in ltxresult)
        self.assertTrue("% %%%ABSTRACT%%%" in ltxresult)
        self.assertTrue("\\end{document}" in ltxresult)

    def testLatexPDF(self):
        """Test Latex document parsing
        """
        simple_report = open(join(settings.MEDIA_ROOT, 'report.tex',), 'r').read()
        ltxdoc = LatexDocument(simple_report)

        pdf = ltxdoc.as_pdf()
        # Manual Checkin : change this
        #open("/tmp/result.pdf", 'w').write(pdf.read())

    def testLatexDocumentAddition(self):
        """Test Latex document Addition
        """
        simple_report = open(join(settings.MEDIA_ROOT, 'report.tex',), 'r').read()
        ltxdoc = LatexDocument(simple_report)
        simple_report2 = open(join(settings.MEDIA_ROOT, 'report2.tex',), 'r').read()
        ltxdoc2 = LatexDocument(simple_report2)

        ltxdoc3 = ltxdoc + ltxdoc2

        self.assertTrue(isinstance(ltxdoc3, LatexDocument))

        # documentclass Test
        self.assertEqual(ltxdoc3.document_class, "report")
        self.assertEqual(len(ltxdoc3.document_class_opts), 2)
        self.assertEqual(ltxdoc3.document_class_opts[1], "11pt")

        # Packages test
        self.assertEqual(len(ltxdoc.packages), 9)
        self.assertTrue('todo' in ltxdoc.packages.keys())

        # Preamble test
        self.assertTrue(ltxdoc3.preamble.index("My title") >= ltxdoc3.preamble.index("Almanach"))

        # Document test
        self.assertTrue(ltxdoc3.document.index("ABSTRACT") <= ltxdoc3.document.index("sport"))

    def testLatexPDF_File(self):
        """Test File inclusion
        """
        simple_report = open(join(settings.MEDIA_ROOT, 'report_image.tex',), 'r').read()

        # By path
        ltxdoc = LatexDocument(simple_report)
        false_imagepath = join(settings.MEDIA_ROOT, 'jango-logo-negative.png',)
        self.assertRaises(OSError, ltxdoc.add_file, false_imagepath, "django.png")
        imagepath = join(settings.MEDIA_ROOT, 'django-logo-negative.png',)
        ltxdoc.add_file(imagepath, "django.png")
        ltxdoc.files[0].name = "django.png"

        pdf = ltxdoc.as_pdf()

        ## {{{ http://code.activestate.com/recipes/496837/ (r1)
        rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)
        self.assertEquals(len(rxcountpages.findall(pdf.read())), 3)
        #open("/tmp/result.pdf", 'w').write(pdf.read())

        # By file
        ltxdoc = LatexDocument(simple_report)
        afile = open(join(settings.MEDIA_ROOT, 'django-logo-negative.png',), 'rb')
        ltxdoc.add_file(afile, "django.png")
        ltxdoc.files[0].name = "django.png"

        pdf = ltxdoc.as_pdf()
        self.assertEquals(len(rxcountpages.findall(pdf.read())), 3)

        # Add 2 tex
        ltxdoc = LatexDocument(simple_report)
        afile = open(join(settings.MEDIA_ROOT, 'django-logo-negative.png',), 'rb')
        ltxdoc.add_file(afile, "django.png")
        ltxdoc.files[0].name = "django.png"

        simple_report2 = open(join(settings.MEDIA_ROOT, 'report2.tex',), 'r').read()
        ltxdoc2 = LatexDocument(simple_report2)

        ltxdoc3 = ltxdoc + ltxdoc2
        pdf = ltxdoc3.as_pdf(debug=True)
        self.assertEquals(len(rxcountpages.findall(pdf.read())), 4)

        # Add 2 tex (inverted)
        ltxdoc = LatexDocument(simple_report)
        afile = open(join(settings.MEDIA_ROOT, 'django-logo-negative.png',), 'rb')
        ltxdoc.add_file(afile, "django.png")
        ltxdoc.files[0].name = "django.png"

        simple_report2 = open(join(settings.MEDIA_ROOT, 'report2.tex',), 'r').read()
        ltxdoc2 = LatexDocument(simple_report2)

        ltxdoc3 = ltxdoc2 + ltxdoc
        pdf = ltxdoc3.as_pdf(debug=True)
        self.assertEquals(len(rxcountpages.findall(pdf.read())), 4)

