#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.plugins.marshals"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules

__all__ = ['TestSections']

# Project dependences
from sleipnir.testing.data import DATA
from sleipnir.testing.test import TestCase, create_suite, run_suite


from sleipnir.heuristics.sections import SectionTSP
from sleipnir.heuristics.sections import SectionError
from sleipnir.heuristics.sections import IterableSection
from sleipnir.heuristics.sections import SectionValue, SectionComment
from sleipnir.heuristics.sections import SectionHeader, SectionContent

DATA = {
    'SECTION_NAME': "TEST_NAME_TYPE",
    'sn': "test_name",
    'sv': "section_value",
    'sc': "section_comment",

    'CONTENT_NAME': "TEST_NAME_SECTION",
    'cn': "test_name",
    'cv': "content_value",
    'cc': "content_comment",
    }


#pylint: disable-msg=R0903,R0904
class TestSections(TestCase):
    """Check for behaviour of Section Class collection"""

    #pylint: disable-msg=C0103
    def setUp(self):
        self.tsp = SectionTSP()
        self.SN = DATA["SECTION_NAME"]
        self.sn = DATA["sn"]
        self.vl = DATA["sv"]

        self.CN = DATA["CONTENT_NAME"]
        self.cn = DATA["cn"]
        self.vc = [DATA["cc"] + str(i) for i in range(0, 10)]

    #pylint: disable-msg=R0201
    def __test_comment(self, sc, comment_value=DATA['sc'], comments=5):
        """Private method to check comments behaviour"""

        for comment in range(comments):
            sc.comments.create(comment_value + str(comment))

        assert len(sc.comments) == comments
        assert isinstance(sc.comments[0], SectionComment)

        for comment in range(comments):
            value = comment_value + str(comment)
            assert sc.comments[comment].type == 'comment'
            assert sc.comments[comment].value == value
            assert sc.comments[comment](str) == value

    def test_comments(self):
        """Verify TSP section has 'comments' collection"""
        assert hasattr(self.tsp, "comments")
        assert not hasattr(self.tsp, 'comment')
        assert not hasattr(self.tsp, 'comment')
        self.__test_comment(self.tsp)

    def test_sections(self):
        """Verify TSP section has 'sections' collection"""
        assert hasattr(self.tsp, "sections")
        assert hasattr(self.tsp.sections, "get")
        assert isinstance(self.tsp.sections, IterableSection)

    def test_section_create_name(self):
        """check for new section creation"""
        # Be sure test section to be creatred not exists
        self.assertRaises(AttributeError, getattr, self.tsp, self.sn)
        self.assertRaises(KeyError, self.tsp.sections.__getitem__, self.sn)
        assert self.tsp.sections.get(self.sn, None) == None

        # create new section
        assert isinstance(self.tsp.sections.create(self.SN), SectionHeader)
        self.assertRaises(SectionError, self.tsp.sections.create, self.SN)

        # check existence
        assert hasattr(self.tsp, self.sn)
        assert not hasattr(self.tsp, self.SN)

        assert isinstance(self.tsp.sections.test_name, SectionHeader)
        assert isinstance(self.tsp.sections[self.sn], SectionHeader)
        assert self.tsp.sections.test_name == self.tsp.sections[self.sn]
        assert self.tsp.test_name.section == self.tsp.sections.test_name
        assert self.tsp.sections.test_name.value == self.SN
        assert self.tsp.sections.test_name.name == self.sn.upper()
        assert self.tsp.sections.test_name.type == 'section'

    def test_section_create_value(self):
        """check for new value creation into an existing section"""
        self.tsp.sections.create(self.SN)
        value = self.tsp.sections.test_name.values.create(self.vl)
        assert value == self.tsp.sections.test_name.values[0]

        assert isinstance(self.tsp.sections.test_name.values[0], SectionValue)
        assert self.tsp.sections.test_name.values[0](str) == self.vl
        assert self.tsp.sections.test_name.values[0].type == 'sec_value'
        assert self.tsp.sections.test_name.values[0].value == self.vl
        assert self.tsp.sections.test_name.values[0](lambda x: x.upper()) == \
            self.vl.upper()

    def test_section_create_comments(self):
        """check comment into an existing section"""
        self.tsp.sections.create(self.SN)
        assert not hasattr(self.tsp.sections[self.sn], 'comment')
        assert not hasattr(self.tsp.test_name.section, 'comment')
        self.__test_comment(self.tsp.sections.test_name)

    def test_section_create_value_comments(self):
        """check for comments creation into a section value section"""
        self.tsp.sections.create(self.SN)
        value = self.tsp.sections.test_name.values.create(self.vl)
        assert not hasattr(value, 'comment')
        self.__test_comment(value)

    def test_contents(self):
        """check for 'contents' section into a TSP section"""
        assert hasattr(self.tsp, "contents")
        assert hasattr(self.tsp.contents, "get")
        assert isinstance(self.tsp.contents, IterableSection)

    def test_contents_create_name(self):
        """check for contents creation"""
        self.assertRaises(AttributeError, getattr, self.tsp, self.cn)
        self.assertRaises(KeyError, self.tsp.contents.__getitem__, self.cn)
        assert self.tsp.contents.get(self.cn, None) == None

        # create new content
        assert isinstance(self.tsp.contents.create(self.CN), SectionContent)
        self.assertRaises(SectionError, self.tsp.contents.create, self.CN)

        # check existence
        assert hasattr(self.tsp, self.cn)
        assert not hasattr(self.tsp, self.CN)

        assert isinstance(self.tsp.contents.test_name, SectionContent)
        assert isinstance(self.tsp.contents[self.cn], SectionContent)
        assert self.tsp.contents.test_name == self.tsp.contents[self.cn]
        assert self.tsp.test_name.content == self.tsp.contents.test_name
        assert self.tsp.contents.test_name.value == self.CN
        assert self.tsp.contents.test_name.name == self.cn.upper()
        assert self.tsp.contents.test_name.type == 'content'

    def test_contents_create_value(self):
        """check for add values to a contents content"""
        self.tsp.contents.create(self.CN)
        for i in self.vc:
            value = self.tsp.contents.test_name.values.create(i)
        for i in range(0, 10):
            value = self.tsp.contents.test_name.values[i]
            assert isinstance(value, SectionValue)
            assert DATA["cc"] + str(i) == value(str) == value.value
            assert value.type == 'content_value'
            assert value(lambda x: x.upper()) == str.upper(DATA["cc"] + str(i))

    def test_content_create_comments(self):
        """check comment into an existing content"""
        self.tsp.contents.create(self.CN)
        assert not hasattr(self.tsp.contents[self.cn], 'comment')
        assert not hasattr(self.tsp.test_name.content, 'comment')
        self.__test_comment(self.tsp.contents.test_name)

    def test_content_create_value_comments(self):
        """check for comments creation into a content value content"""
        self.tsp.contents.create(self.CN)
        for i in self.vc:
            value = self.tsp.contents.test_name.values.create(i)
            assert not hasattr(value, 'comment')
            self.__test_comment(value)

    def test_sections_compare(self):
        """check if compare sections works"""
        self.tsp1, self.tsp2 = SectionTSP(), SectionTSP()
        assert self.tsp == self.tsp
        assert self.tsp == self.tsp1
        assert self.tsp == self.tsp2

        assert id(self.tsp1) != id(self.tsp2)
        section1 = self.tsp1.sections.create(self.SN)
        section2 = self.tsp2.sections.create(self.SN)
        assert section1 == section2
        assert self.tsp1 == self.tsp2
        assert self.tsp1 != self.tsp

        # minimal test
        content1 = self.tsp1.contents.create(self.CN)
        content2 = self.tsp2.contents.create(self.CN)
        assert section1 == section2
        assert self.tsp1 == self.tsp2
        assert self.tsp1 != self.tsp

        # sections MUST be created in sync
        self.tsp1 = SectionTSP()
        section11 = self.tsp1.sections.create(self.SN)
        section12 = self.tsp1.sections.create("OTHER" + self.SN)
        self.tsp2 = SectionTSP()
        section21 = self.tsp2.sections.create(self.SN)
        section22 = self.tsp2.sections.create("OTHER" + self.SN)
        assert section11 == section21
        assert section12 == section22
        assert self.tsp1 == self.tsp2

        # change section creation order
        section14 = self.tsp1.sections.create("1" + self.SN)
        section23 = self.tsp2.sections.create("2" + self.SN)
        section13 = self.tsp1.sections.create("2" + self.SN)
        section24 = self.tsp2.sections.create("1" + self.SN)
        assert section13 == section23
        assert section14 == section24
        assert self.tsp1 != self.tsp2

    def test_section_contents_lifecicle(self):
        """check section lifecicle"""
        section = self.tsp.sections.create(self.SN)
        content = self.tsp.contents.create(self.CN)

        # both has as parent a SectionContainer
        assert id(section) != id(content)
        assert id(section.parent) == id(content.parent)
        assert type(section) in (SectionHeader,)
        assert type(content) in (SectionContent,)

        assert len(self.tsp.sections) == 1
        assert len(self.tsp.contents) == 1

        for cnt in self.tsp:
            len(cnt) == 1

        # And section ancestor is Root TSP Section
        assert type(section.parent.parent) in (SectionTSP,)

        # Section Container has 2 childs, a SectionHeader
        # and a SectionContainer
        assert len(section.parent) == len(content.parent) == 2

        # We also can remove contents and sections.
        #If we do that, section TSP will be empty
        parent = section.parent
        self.tsp.sections.remove(section)
        assert None == section.parent
        assert len(content.parent) == 1
        self.tsp.contents.remove(content)
        content.parent = None
        assert len(parent) == 0
        assert len(self.tsp) == 0

        # now  readd sections
        self.tsp.add(section)
        self.tsp.add(content)
        assert len(self.tsp) == 1
        self.tsp.remove(section.parent)
        assert len(self.tsp) == 0


#pylint: disable-msg=C0103
main_suite = create_suite([TestSections, ])

if __name__ == '__main__':
    # pylint: disable-msg=E1120
    run_suite()
