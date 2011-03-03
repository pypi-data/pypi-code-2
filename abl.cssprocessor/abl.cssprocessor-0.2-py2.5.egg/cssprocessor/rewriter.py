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
from functools import wraps
import codecs
import logging
import pprint
from collections import defaultdict


from pyparsing import originalTextFor, ParseException

from .parser import (
    CSSParser,
    StringNode,
    URINode,
    )

from .util import Replacer

logger = logging.getLogger(__name__)



def delegate_action(func):
    @wraps(func)
    def _wrapper(self, input, start, tokens):
        if self.delegate is not None and hasattr(self.delegate, func.func_name):
            try:
                return getattr(self.delegate, func.func_name)(input, start, tokens)
            except:
                raise Exception(repr(sys.exc_info()[1]) + repr(tokens))

    return _wrapper


class RewriteParser(CSSParser):


    def __init__(self, delegate=None):
        super(RewriteParser, self).__init__()
        self.delegate = delegate
        self.import_.setParseAction(self.import_parse_action)
        self.import_location.setParseAction(self.import_location_parse_action)
        self.declaration.setParseAction(self.declaration_parse_action)
        self.declaration_value.setParseAction(self.declaration_value_parse_action)
        # using add here because we want to keep the original
        self.charset_declaration.addParseAction(self.charset_declaration_action)


    @delegate_action
    def import_parse_action(self, input, start, tokens):
        pass


    @delegate_action
    def import_location_parse_action(self, input, start, tokens):
        pass


    @delegate_action
    def declaration_parse_action(self, input, start, tokens):
        pass


    @delegate_action
    def declaration_value_parse_action(self, input, start, tokens):
        pass


    @delegate_action
    def charset_declaration_action(self, input, start, tokens):
        pass



class CSSReference(object):

    def __init__(self, rewriter, filename):
        self.filename = filename
        self.dir = filename.dirname()
        self.rewriter = rewriter


    def exists(self):
        return self.filename.exists()


    def basename(self):
        return self.filename.basename()


    def copy(self, other):
        return self.filename.copy(other)


    def splitext(self):
        return self.filename.splitext()


    def md5(self):
        return self.filename.md5()


    def __hash__(self):
        return hash(str(self.filename))


    def __eq__(self, other):
        return str(self.filename) == str(other.filename)


    def __lt__(self, other):
        return str(self.filename) < str(other.filename)


    def __repr__(self):
        return repr(self.filename)


    def __str__(self):
        return str(self.filename)



class CSSImage(CSSReference):


    def __init__(self, rewriter, filename):
        super(CSSImage, self).__init__(rewriter, filename)
        # the CSS that link to this image
        self.referrers = set()


    def add_referrer(self, css):
        self.referrers.add(css)


    def rewritten_url(self):
        return self.rewriter.rewritten_url(self)




class CSSFile(CSSReference):


    def __init__(self, rewriter, filename, dependencies=()):
        super(CSSFile, self).__init__(rewriter, filename)
        self.unique_name = None

        if self.filename.exists():
            # get the encoding & read the files contents
            # based on that
            charset = "utf-8"
            content = self.filename.open().read()
            if "@charset" in content:
                parser = CSSParser()
                # try & parse a possible charset_declaration
                parser.charset_declaration.parseString(content[:content.index(";")+1], False)
                charset = parser.charset
            self.content = content.decode(charset)
            self.replacer = Replacer(self.content)
            self._replaced_content = None
        self.import_locations = []
        # other CSS referred from this CSS
        self.references = set(dependencies)


    def get_output(self, unix_newlines=False):
        if self._replaced_content is None:
            self._replaced_content = self.replacer.get_value()
            if unix_newlines:
                self._replaced_content = self._replaced_content.replace("\r\n", "\n")
        return self._replaced_content


    def process(self):
        parser = RewriteParser(delegate=self)
        parser.parseString(self.content, True)


    def charset_declaration_action(self, input, loc, tokens):
        # remove the charset declaration, we have utf-8 only
        start, end = tokens[0], tokens[-1]
        self.replacer[start:end] = ""


    def import_parse_action(self, input, start, tokens):
        start, end = tokens[0], tokens[-1]
        tokens = tokens[1:-1]
        position = slice(start, end)
        location = self.import_locations.pop()

        if isinstance(location, StringNode):
            # this *must* be a relative reference,
            # so resolve it
            self.references.add(self.rewriter.add_css(self.filename.dirname() / location.content))
            # and we can safely remove that location
            self.replacer[position] = ""
        elif isinstance(location, URINode):
            if location.relative:
                self.references.add(self.rewriter.add_css(self.filename.dirname() / location.path))
                self.replacer[position] = ""


    def import_location_parse_action(self, input, start, tokens):
        self.import_locations.append(tokens[0])


    def declaration_parse_action(self, input, loc, tokens):
        property_ = tokens[0]
        if property_ in ("background", "background-image"):
            uris = [uri for uri in tokens if isinstance(uri, URINode)]
            if not uris:
                return
            assert len(uris) == 1
            image_url = uris[0]
            if image_url.relative:
                img = self.rewriter.add_image(self.dir / image_url.path)
                img.add_referrer(self)
                if img.exists():
                    self.replacer[image_url.position] = img.rewritten_url


    @classmethod
    def disambiguate_names(cls, css_files):
        """
        Creates a sorting-criteria that will not depend on
        the *full* filenames, but instead only so much of the
        paths as is needed to disambiguate them.
        """
        name_mapping = defaultdict(list)
        working_list = list(css_files)
        level = 1

        def get_name(css_file):
            parts = []
            for _ in xrange(level):
                css_file, right = css_file.split()
                parts.append(right)
            return "/".join(reversed(parts))
        while working_list:
            for css_file in working_list:
                name = get_name(css_file.filename)
                name_mapping[name].append(css_file)

            working_list[:] = []

            for key, value in name_mapping.iteritems():
                if len(value) == 1:
                    value[0].unique_name = key
                else:
                    working_list.extend(value)
            level += 1
            name_mapping.clear()

        for css_file in css_files:
            assert css_file.unique_name is not None, css_file


class SimpleCopyImagePreprocessor(object):


    def process(self, images, basedir, images_path):
        """
        Gets a list of images, and returns a mapping
        of them to their urls.

        Only overwrites images in the destination which
        already exist if they happen to have a differing
        md5-sum.
        """
        res = {}
        for img in images:
            img_md5 = img.md5()
            dest = images_path / img.basename()
            if dest.exists() and dest.md5() != img_md5:
                prefix, ext = img.splitext()
                count = 1
                while True:
                    basename = "%s-%i%s" % (prefix, count, ext)
                    dest = (images_path / basename)
                    if dest.exists() and dest.md5() == img_md5:
                        break
                    if not dest.exists():
                        break
                    count += 1
            if not dest.exists():
                img.copy(dest)
            res[img] = str(dest)[len(str(basedir))+1:] # plus the path-sep
        return res


class MD5ImagePreprocessor(object):


    def process(self, images, basedir, images_path):
        res = {}
        for img in images:
            _, ext = img.splitext()
            dest = images_path / ("%s%s" % (img.md5(), ext))
            if not dest.exists():
                img.copy(dest)
            res[img] = str(dest)[len(str(basedir))+1:] # plus the path-sep
        return res



class CSSRewriter(object):


    def __init__(self,
                 output,
                 images_path="images",
                 image_processor=None,
                 unix_newlines=True,
                 ):
        if image_processor is None:
            image_processor = SimpleCopyImagePreprocessor()
        self.image_processor = image_processor

        self.unix_newlines = unix_newlines
        self.output = output
        self.images_path = self.output.dirname() / images_path
        if self.images_path.exists():
            assert self.images_path.isdir()
        else:
            self.images_path.mkdir()
        self.all_css = set()
        self.css_to_process = []
        self.non_existing = set()
        self.images = {}
        self.image_paths = {}


    def add_css(self, css_file, dependencies=()):
        def process_css(css):
            if css not in self.all_css:
                self.all_css.add(css)
                if not css.exists():
                    self.non_existing.add(css)
                else:
                    self.css_to_process.append(css)
                self.work()
            # we need to return the exact same instance
            return [c for c in self.all_css if css == c][0]

        deps = set()
        for dep in dependencies:
            dep = CSSFile(self, dep)
            dep = process_css(dep)
            deps.add(dep)

        css = CSSFile(self, css_file, deps)
        return process_css(css)


    def add_image(self, imagefile):
        img = CSSImage(self, imagefile)
        if img not in self.images:
            self.images[img] = img
        return self.images[img]


    def work(self):
        while self.css_to_process:
            next_css, self.css_to_process = self.css_to_process[0], self.css_to_process[1:]
            next_css.process()


    def topological_order(self):
        # this is needed so that the sort is stable over
        # various machines
        CSSFile.disambiguate_names(self.all_css)

        def by_unique_name(cf):
            return cf.unique_name

        all_ = sorted(set(css for css in self.all_css if css not in self.non_existing), key=by_unique_name)
        L = []
        S = all_ #set(all_)
        # build up the inverse relationship of edges,
        # as our algorithm works better with these,
        for css in all_:
            css.incoming = []

        for css in all_:
            for adjacence in css.references:
                if adjacence in all_ and css not in adjacence.incoming:
                    adjacence.incoming.append(css)

        S = sorted(set(css for css in all_ if not css.incoming), key=by_unique_name)
        assert S, "Cyclic graph of CSS!"
        while S:
            S.sort()
            n = S.pop()
            L.append(n)
            for m in n.references:
                # no non-existing css-files
                if m in all_:
                    m.incoming.remove(n)
                    if not m.incoming and m not in S:
                        S.append(m)

        if set(css for css in all_ if css.incoming):
            raise Exception("At least one cycle")
        return L


    def rewritten_url(self, img):
        return "url(%s)" % self.image_path_mapping[img]


    def rewrite(self):
        # first, pre-process and copy the images
        # into their destination to get their
        # final relative url.

        basedir = self.output.directory()

        images = []
        for img in self.images.values():
            if not img.exists():
                logger.warn("Image '%r' couldn't be found!", img)
            else:
                images.append(img)
        self.image_path_mapping = self.image_processor.process(images,
                                                               basedir,
                                                               self.images_path
                                                               )

        for css in self.non_existing:
            logger.warn("CSS file '%r' couldn't be found!", css)


        with self.output.open("w") as outf:
            L = reversed(self.topological_order())
            for css in L:
                outf.write("\n/* ---- %s ---- */\n" % css.unique_name)
                outf.write(css.get_output(self.unix_newlines).encode("utf-8"))



