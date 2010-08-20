# -*- coding: iso-8859-1 -*-
"""
	MoinMoin - XML Source Parser

    @copyright: 2005 by Davin Dubeau <davin.dubeau@gmail.com>
    @license: GNU GPL, see COPYING for details.

"""

from MoinMoin.util.ParserBase import ParserBase

Dependencies = []

class Parser(ParserBase):

    parsername = "ColorizedXML"
    extensions = ['.xml']
    Dependencies = []

    def setupRules(self):
        ParserBase.setupRules(self)
                
        self.addRulePair("Comment","<!--","-->")
        self.addRule("Number",r"[0-9]+")
        self.addRule("SPChar","[=<>/\"]")
        self.addRule("ResWord","(?!<)[\w\s]*(?![\w=\"])?(?![\w\s\.<])+(?!>)*")