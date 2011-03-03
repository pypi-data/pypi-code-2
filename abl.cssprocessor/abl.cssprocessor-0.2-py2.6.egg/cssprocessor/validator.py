"""
Copyright (c) 2009 Ableton AG

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import, with_statement

import sys
import pprint
from textwrap import dedent

import argparse
from pyparsing import ParseException

from abl.vpath.base import URI

from .parser import URINode
from .rewriter import RewriteParser




class CSSValidator(object):


    def __init__(self, filename, verbose=False, roots=()):
        self.filename = filename

        root_mapping = []
        for path in roots:
            if isinstance(path, tuple):
                # for testing, you can pass the mapping as (prefix, URI)
                root_mapping.append(path)
            else:
                if ":" in path:
                    prefix, path = path.split(":", 1)
                else:
                    prefix = "/"
                assert path.startswith("/"), "%s must start with /"
                root_mapping.append((prefix, URI("file://%s" % path)))

        self.root_mapping = root_mapping
        self.verbose = verbose
        self.warnings = []


    def validate(self):
        if not self.filename.exists() or self.filename.isdir():
            self.error("No such file: %r" % self.filename)

        self.relative_base = self.filename.directory()
        self.report("Attempting to parse CSS file %s" % self.filename)
        parser = RewriteParser(self)
        with self.filename.open() as inf:
            content = inf.read()
        try:
            res = parser.parseString(content)
        except ParseException, e:
            message = "ERROR: Malformed CSS, text is: <<<%s>>>" % e.pstr
            self.warnings.append(message)
            print message



    def declaration_parse_action(self, input, loc, tokens):
        property_ = tokens[0]
        if property_ in ("background", "background-image"):
            uris = [uri for uri in tokens if isinstance(uri, URINode)]
            if not uris:
                return
            assert len(uris) == 1
            image_url = uris[0]
            path = image_url.path
            if image_url.relative:
                if not (self.relative_base / path).exists():
                    self.warning("Relative resource not found: %s" % path)
            else:
                if not self.check_for_absoulte_resource(path):
                    self.warning("Absolute resource not found: %s" % path)


    def check_for_absoulte_resource(self, resource_path):
        for prefix, path in self.root_mapping:
            if resource_path.startswith(prefix):
                rest = resource_path[len(prefix):]
                if rest.startswith("/"):
                    rest = rest[1:]
                if (path / rest).exists():
                    return True
        return False


    def error(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.exit(1)


    def report(self, msg):
        if self.verbose:
            print msg


    def warning(self, msg):
        self.warnings.append(msg)
        print "WARNING:", msg


def validator():
    parser = argparse.ArgumentParser()
    parser.add_argument("cssfile",
                        help=dedent("""
                        The CSS-file to validate.
                        """),
                        )

    parser.add_argument("--root",
                        help=dedent("""
                        To resolve absolute paths, you need to give
                        at least on root-path.

                        You can specify several.

                        It's also possible to give a prefix by using
                        a colon.

                        So

                          --root=/resources:/home/user/project/public/resources

                        will be used to resolve resources that start with '/resources'.
                        """),
                        action="append",
                        dest="roots",
                        default=[],
                       )
    parser.add_argument("-v", "--verbose", action="store_true",
                        default=False,)



    args = parser.parse_args(sys.argv[1:])


    validator = CSSValidator(URI("file://%s" % args.cssfile),
                             roots=args.roots,
                             verbose=args.verbose,
                             )

    validator.validate()

