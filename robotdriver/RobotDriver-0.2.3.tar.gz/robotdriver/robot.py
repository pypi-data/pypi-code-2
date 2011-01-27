# -*- coding: utf-8 -*-

__docformat__ = 'restructuredtext en'

from xml.etree.cElementTree import Element, parse
import os

from bitten.api import IReportChartGenerator, IReportSummarizer
from bitten.util import xmlio
from trac.core import *
from trac.web.chrome import ITemplateProvider
import pkg_resources


class RobotFrameworkReportParser:
    def __init__(self, xml_file=None):
        self.xml = xml_file

        self.root = None
        self.feed(self.xml)

    def feed(self, xml_file):
        if xml_file:
            self.root = parse(xml_file).getroot()
        return self

    def parse(self):
        if not self.root:
            return

        for suite in self.root.findall('suite'):
            suite_source = suite.get('source')
            self.top_dir = os.path.dirname(suite_source) + os.path.sep
            for case in self._parse_suite(suite, '', suite_source):
                yield case

    def _parse_suite(self, suite, parent_name, suite_source):
        if parent_name:
            suite_name = '%s :: %s' % (parent_name, suite.get('name'))
        else:
            suite_name = suite.get('name')
        for case in self._walk_node(suite, suite_name, suite_source):
            yield case

    def _walk_node(self, suite, suite_name, suite_source):
        for child in suite.getchildren():
            if child.tag == 'test':
                for case in self._parse_testcase(child, suite_name,
                        suite_source):
                    yield case
            elif child.tag == 'suite':
                source = child.get('source')
                for case in self._parse_suite(child, suite_name, source):
                    yield case

    def _parse_testcase(self, suite, parent_name, source):
        suite_name = '%s :: %s' % (parent_name, suite.get('name'))
        status_node = suite.find('status')
        test_type = suite.get('type')
        related_suite_source = source.replace(self.top_dir, '')
        if test_type in ['setup', 'teardown']:
            return
        if status_node is not None:
            status = status_node.get('status')
            text = status_node.text or ''
            yield status, related_suite_source, suite_name, text
        for case in self._walk_node(suite, suite_name, source):
            yield case

def robot(ctxt, file_=None):
    """Extract data from a ``pybot`` report.

    :param ctxt: the build context
    :type ctxt: `Context`
    :param file\_: name of the file containing the pybot report
    """
    assert file_, 'Missing required attribute "file"'

    results = xmlio.Fragment()

    for case in RobotFrameworkReportParser(ctxt.resolve(file_)).parse():
        status, source, suite_name, message = case
        testcase = xmlio.Element('robot', status=status.encode('utf-8'),
                               source=source.encode('utf-8'),
                               suite_name=suite_name.encode('utf-8'),
                               message=message.encode('utf-8'))
        results.append(testcase)
    ctxt.report('robot', results)


class RobotDriverSummarizer(Component):
    implements(IReportSummarizer)

    def get_supported_categories(self):
        return ['robot']

    def render_summary(self, req, config, build, step, category):
        assert category == 'robot'

        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""
SELECT item_file.value AS file,
       COUNT(item_success.value) AS num_success,
       COUNT(item_ignore.value) AS num_ignore,
       COUNT(item_failure.value) AS num_failure,
       COUNT(item_error.value) AS num_error
FROM bitten_report AS report
 LEFT OUTER JOIN bitten_report_item AS item_file
  ON (item_file.report=report.id AND item_file.name='source')
 LEFT OUTER JOIN bitten_report_item AS item_success
  ON (item_success.report=report.id AND item_success.item=item_file.item AND
      item_success.name='status' AND item_success.value='PASS')
 LEFT OUTER JOIN bitten_report_item AS item_ignore
  ON (item_ignore.report=report.id AND item_ignore.item=item_file.item AND
      item_ignore.name='status' AND item_ignore.value='IGNORE')
 LEFT OUTER JOIN bitten_report_item AS item_failure
  ON (item_failure.report=report.id AND item_failure.item=item_file.item AND
      item_failure.name='status' AND item_failure.value='FAIL')
 LEFT OUTER JOIN bitten_report_item AS item_error
  ON (item_error.report=report.id AND item_error.item=item_file.item AND
      item_error.name='status' AND item_error.value='ERROR')
WHERE category='robot' AND build=%s AND step=%s
GROUP BY file
ORDER BY file""", (build.id, step.name))

        files = []
        total_success, total_ignore, total_failure, total_error = 0, 0, 0, 0
        for file, num_success, num_ignore, num_failure, num_error in cursor:
            files.append({
                'file': file,
                'href': req.href.browser(config.path, file),
                'num_success': num_success,
                'num_ignore': num_ignore,
                'num_failure': num_failure,
                'num_error': num_error,
                })
            total_success += num_success
            total_ignore += num_ignore
            total_failure += num_failure
            total_error += num_error

        data = {'files': files,
                'totals': {'success': total_success,
                           'ignore': total_ignore,
                           'failure': total_failure,
                           'error': total_error}
               }
        return 'bitten_summary_robot.html', data

class RobotDriverChrome(Component):
    implements(ITemplateProvider)

    def get_htdocs_dirs(self):
        """Return the directories containing static resources."""
        return [('robotdriver',
            pkg_resources.resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the directories containing templates."""
        return [pkg_resources.resource_filename(__name__, 'templates')]
