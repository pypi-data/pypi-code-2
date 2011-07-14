# -*- coding: utf-8 -*-

import sys
import os
import shutil
import tempfile
import unittest

from datetime import datetime

from turbogears import config
from turbogears.command.i18n import InternationalizationTool

tool = None

TEMPLATE = """
<html xmlns:py="http://purl.org/kid/ns#">
<head>
    <link py:strip="1" py:for="css in tg_css">${css.display()}</link>
    <link py:strip="1" py:for="js in tg_js_head">${js.display()}</link>
</head>
<body>
  <div>Some text to be i18n'ed</div>
  <div>This is text that has a kid-expression ${_('which is to be i18n')}</div>
  <div foo="${_('kid expression in attribute')}"/>
  <div foo="normal attribute text"/>
  <div lang="en">This is english, and it shouldn't be collected</div>
  <div lang="de">Dies ist Deutsch, und es sollte nicht aufgesammelt werden</div>
  <div>These are some entities that we shouldn't complain about: &nbsp;</div>
</body>
</html>
"""

class I18nToolTest(unittest.TestCase):
    """Test for the tg-admin i18n tool."""

    def setUp(self):
        global tool
        tool = InternationalizationTool('1.1')
        self.work_dir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.work_dir, 'src')
        self.locale_dir = os.path.join(self.work_dir, 'locale')
        os.mkdir(self.src_dir)
        config.update({
            'i18n.locale_dir': self.locale_dir,
            'i18n.domain': 'testmessages',
        })

    def tearDown(self):
        shutil.rmtree(self.work_dir)

    # XXX: these aren't really unit tests, rather functional tests.
    # Unfortunately the InternationalizationTool would need to be seriously
    # refactored to allow this.

    def test_collect_js_strings_utf8(self):
        """Strings from JS files with non-ascii chars (UTF-8) are collected correctly"""
        js_file = os.path.join(self.src_dir, "utf8.js")
        tf = open(js_file, "w")
        tf.write(u"msg = _('Schöne Grüße')".encode('utf-8'))
        tf.close()
        sys.argv = ['i18n.py', '--src-dir', self.src_dir, 'collect']
        tool.load_config = False
        tool.options, dummy = tool.parse_args()
        os.mkdir(self.locale_dir)
        tmp_handle, tmp_potfile = tempfile.mkstemp('.pot', 'tmp', self.locale_dir)
        tool.scan_js_files(tmp_potfile, [js_file])
        pot_content = os.read(tmp_handle, 999).decode('utf-8')
        os.close(tmp_handle)
        os.remove(tmp_potfile)
        os.rmdir(self.locale_dir)
        assert u'Schöne Grüße' in pot_content

    def test_collect_js_strings_latin1(self):
        """Strings from JS files with non-ascii chars (Latin-1) are collected correctly"""
        js_file = os.path.join(self.src_dir, "utf8.js")
        tf = open(js_file, "w")
        tf.write(u"msg = _('Schöne Grüße')".encode('latin1'))
        tf.close()
        sys.argv = ['i18n.py', '--src-dir', self.src_dir, '--js-encoding', 'latin1', 'collect']
        tool.load_config = False
        tool.options, dummy = tool.parse_args()
        os.mkdir(self.locale_dir)
        tmp_handle, tmp_potfile = tempfile.mkstemp('.pot', 'tmp', self.locale_dir)
        tool.scan_js_files(tmp_potfile, [js_file])
        pot_content = os.read(tmp_handle, 999).decode('utf-8')
        os.close(tmp_handle)
        os.remove(tmp_potfile)
        os.rmdir(self.locale_dir)
        assert u'Schöne Grüße' in pot_content

    def test_collect_template_strings(self):
        """Verify the locale directory got created as needed."""
        tf = open(os.path.join(self.src_dir, "test.kid"), "w")
        tf.write(TEMPLATE)
        tf.close()
        assert not os.path.isdir(self.locale_dir), "locale directory should not exist yet"
        sys.argv = ['i18n.py', '--src-dir', self.src_dir, 'collect']
        tool.load_config = False
        tool.run()
        assert os.path.isdir(self.locale_dir), "locale directory not created"
        tf = open(os.path.join(self.locale_dir, "testmessages.pot"))
        pot_content = tf.read()
        tf.close()
        assert "Some text to be i18n'ed" in pot_content
        assert "kid expression in attribute" in pot_content
        assert "normal attribute text" not in pot_content
        assert "it shouldn't be collected" not in pot_content
        assert "es sollte nicht aufgesammelt werden" not in pot_content
