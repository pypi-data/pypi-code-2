from handcrank.tests.testcase import TestCase
from handcrank.report import Report


class ReportTest(TestCase):
    def test_can_create_and_dump(self):
        Report(
            from_dir='/somewhere',
            tmp_dir='/somewhere',
            out_dir='/somewhere',
            generated_count=0,
            source_count=0,
            entry_point=None).dump()
