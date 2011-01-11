"""Code builder of presentation logic"""

# First Created: 2010-12-29 10:21:25 +0900
# Last Modified: 2011-01-12 00:28:52 +0900

# Copyright (c) 2010 Naoya Inada<naoina@naniyueni.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import ast
import copy
import os.path as path
import sys

from io import StringIO

from . import (TenpyConfig, etree, cache)
from .etree import (cssselect, E, A)
from .parser import TenpyFile
from .util import flatten

__author__ = "Naoya Inada <naoina@naniyueni.org>"

__all__ = [
        "TenpyBuilder"
        ]


TENPY_WRAP_TAG = "__tenpy_wrap_tag__"


class NotTenpyTargetException(Exception):
    pass

class UnsupportedResultException(Exception):
    pass


class TenpyBuilder:

    def __init__(self, config=None):
        if not config:
            config = TenpyConfig()
        if config["cache"]:
            self._codecache = cache.CodeCache()
            self._pagecache = cache.PageCache()
        else:
            self._codecache = cache.NullCodeCache()
            self._pagecache = cache.NullPageCache()
        self.config = config
        self.tenpy = TenpyFile()
        self.sfunc = {
                "css":   self._selector_css,
                "xpath": self._selector_xpath,
                }

    def build(self, filename, **variables):
        cachename = filename + variables.__str__()
        try:
            result = self._pagecache[cachename]
        except KeyError:
            with open(filename) as f:
                text = f.read()
                file = self._find_tenpy_file(filename)
                if not file:
                    return text

                files = []
                default_file = self._find_tenpy_file(self.config["default_tenpy_page"]
                        + self.config["template_extensions"][0])
                if default_file:
                    files.append(path.normpath(default_file))
                files.append(path.normpath(file))

                result = self._build_target(text, files, **variables)
                self._pagecache[cachename] = result
        return result

    def _build_target(self, text, files, **variables):
        element = self._prepare_etree(text)
        for f in files:
            for stype, selector, code in self.tenpy.parse(f):
                func = self._genfunc(code, f, selector, **variables)
                for e in self.sfunc[stype](element, selector):
                    try:
                        func(**variables)
                    except NameError as e:
                        raise NameError(e.__str__() + ' in "' + selector + '", File "' + f + '"')
                    result = self._get_result_elements(func(**variables), e, selector, f)
                    result.tail = e.tail
                    e.getparent().replace(e, result)
        return self._restore_text(element)

    def _selector_css(self, element, selector):
        select = cssselect.CSSSelector(selector)
        return select(element)

    def _selector_xpath(self, element, selector):
        prefix = "" if selector.startswith("/") else "//"
        select = etree.XPath(prefix + selector)
        return select(element)

    def _get_result_elements(self, code, e, selector, fname):
        element = etree.Element(TENPY_WRAP_TAG)
        if isinstance(code, str):
            element.text = code
        elif isinstance(code, list):
            element.extend([self._get_result_elements(x, e, selector, fname) for x in code])
        elif isinstance(code, dict):
            tmp_elem = etree.Element(TENPY_WRAP_TAG)
            tmp_elem.extend([copy.deepcopy(child) for child in e])
            for selector, inner_code in code.items():
                (selector, stype) = self.tenpy.parse_selector(selector)
                replfunc = self._replfunc(inner_code)
                inner_code = self._get_result_elements(inner_code, e, selector, fname)
                for inner_elem in self.sfunc[stype](tmp_elem, selector):
                    replfunc(inner_elem, inner_code)
                element.append(tmp_elem)
        elif isinstance(code, etree._Element):
            element.append(code)
        elif isinstance(code, etree._Attribute):
            for a, v in code.__dict__.items():
                if v is None:
                    del e.attrib[a]
                else:
                    e.attrib[a] = v
            element.append(copy.deepcopy(e))
        else:
            raise UnsupportedResultException(
                    "unsupported result type {} in `{}` of {}".format(
                        str(type(code)), selector, path.relpath(fname)))
        return element

    def _replfunc(self, code):
        if isinstance(code, str):
            return lambda a, b: setattr(a, "text", b.text)
        elif isinstance(code, list) or isinstance(code, dict):
            return lambda a, b: a.getparent().replace(a, b)

    def _genfunc(self, code, *seeds, **variables):
        name = self._codecache.cachename(*seeds)
        try:
            result = self._codecache[name]
        except KeyError:
            aobj = ast.parse(code)
            aret = aobj.body[-1]

            if not isinstance(aret, ast.Expr):
                raise SyntaxError("last line must be expression")

            aobj.body[-1] = ast.Return(aret.value, lineno=aret.lineno,
                    col_offset=aret.col_offset)
            args = ast.arguments([ast.arg(a, None) for a in variables], None,
                    None, [], None, None, [], [])
            afunc = ast.FunctionDef(name, args, aobj.body, [], None, lineno=0,
                    col_offset=0)
            aobj.body = [afunc]
            exec(compile(aobj, "<ast>", "exec"))
            result = eval(name)
            self._codecache[name] = result
        return result

    def _prepare_etree(self, text):
        return etree.fromstring("<tenpyroot>" + text + "</tenpyroot>")

    def _restore_text(self, elem):
        etree.strip_tags(elem, TENPY_WRAP_TAG)
        result = elem.text if elem.text else ""
        for e in elem.getchildren():
            result += etree.tostring(e)
        return result

    def _find_tenpy_file(self, filename):
        page, ext = path.splitext(filename)
        if ext not in self.config["template_extensions"]:
            raise NotTenpyTargetException(filename + " is not target extension")

        filedir = path.dirname(page)
        pagename = path.basename(page)
        filepath = self.config["tenpy_file"].format(page=pagename,
                tenpy_extension=self.config["tenpy_extension"])
        for d in self.config["tenpy_filepaths"]:
            if path.isabs(d):
                filepath = path.join(d, filepath)
            else:
                filepath = path.join(filedir, d, filepath)
            if path.isfile(filepath):
                return filepath
        return None
