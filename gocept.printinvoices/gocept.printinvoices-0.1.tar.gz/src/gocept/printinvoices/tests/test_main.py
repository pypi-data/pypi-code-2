# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import doctest
import gocept.printinvoices.main
import os
import os.path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


default_optionflags = doctest.REPORT_NDIFF


def assertOutputChecker(expected, got, optionflags=0):
    optionflags = default_optionflags | optionflags
    output_checker = doctest.OutputChecker()
    assert output_checker.check_output(expected, got, optionflags), \
        output_checker.output_difference(
        doctest.Example('', expected), got, optionflags)


def test_resource(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class Base(unittest.TestCase):

    def setUp(self):
        self.log_dir = tempfile.mkdtemp()
        self.bin_dir = tempfile.mkdtemp()
        self.orig_path = os.environ['PATH']
        os.environ['PATH'] = '%s:%s' % (self.bin_dir, self.orig_path)

    def tearDown(self):
        os.environ['PATH'] = self.orig_path
        shutil.rmtree(self.bin_dir)
        shutil.rmtree(self.log_dir)

    def create_script(self, name, content):
        path = os.path.join(self.bin_dir, name)
        script = open(path, 'w')
        script.write(content)
        script.close()
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)


class PSTest(Base):

    def create_process_ps(self):
        self.create_script('process-ps', """\
#!%(executable)s
import sys
sys.path[0:0] = %(python_path)r
import gocept.printinvoices.main
gocept.printinvoices.main.process_ps()
""" % dict(executable=sys.executable, python_path=sys.path))

    def test_implementation(self):
        input_ps = open(test_resource('input.ps'))
        output_stream = StringIO.StringIO()
        gocept.printinvoices.main.process_ps_implementation(
            1, 4, input_ps, output_stream)
        output_ps = open(test_resource('output.ps'))
        assertOutputChecker(output_ps.read(), output_stream.getvalue())

    def test_end_to_end_pipe(self):
        self.create_process_ps()
        output_path = os.path.join(self.log_dir, 'output.ps')
        output = open(output_path, 'w')
        subprocess.call(
            'process-ps 1 4'.split(),
            stdin=open(test_resource('input.ps')), stdout=output)
        output.close()
        self.assertEqual(
            open(test_resource('output.ps')).read(), open(output_path).read())

    def test_end_to_end_files(self):
        self.create_process_ps()
        output_path = os.path.join(self.log_dir, 'output.ps')
        subprocess.call(
            ('process-ps 1 4 %s %s' %
             (test_resource('input.ps'), output_path)).split())
        self.assertEqual(
            open(test_resource('output.ps')).read(), open(output_path).read())


class PDFTest(Base):

    def setUp(self):
        super(PDFTest, self).setUp()
        # mock lpr so it tells us its calling parameters and input on stdin
        self.create_script('lpr', """\
#!/bin/sh
echo -n $@ > %(log_dir)s/args
cat > %(log_dir)s/input
""" % dict(log_dir=self.log_dir))

    def test_implementation(self):
        gocept.printinvoices.main.process_pdf_implementation(
            1, 4, test_resource('rechnung.pdf'), 'nana_raw')
        self.assertEqual(
            '-P nana_raw', open(os.path.join(self.log_dir, 'args')).read())
        self.assertEqual(
            open(test_resource('output.ps')).read(),
            open(os.path.join(self.log_dir, 'input')).read())

    def test_end_to_end(self):
        self.create_script('process-pdf', """\
#!%(executable)s
import sys
sys.path[0:0] = %(python_path)r
import gocept.printinvoices.main
gocept.printinvoices.main.process_pdf()
""" % dict(executable=sys.executable, python_path=sys.path))
        subprocess.call(
            ('process-pdf 1 4 %s nana_raw' % test_resource('rechnung.pdf')
             ).split())
        self.assertEqual(
            '-P nana_raw', open(os.path.join(self.log_dir, 'args')).read())
        self.assertEqual(
            open(test_resource('output.ps')).read(),
            open(os.path.join(self.log_dir, 'input')).read())
