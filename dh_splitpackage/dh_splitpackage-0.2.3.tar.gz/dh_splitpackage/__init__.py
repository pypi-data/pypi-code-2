# Copyright (C) 2011 Canonical
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This file is part of dh_splitpackage.
#
# dh_splitpackage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation
#
# dh_splitpackage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dh_splitpackage.  If not, see <http://www.gnu.org/licenses/>.

"""
dh_splitpackage - split monolithic installation directory into sub-packages

For more information see the manual page for dh_splitpackage(1) which is
available in debhelper-splitpackage-doc.
"""

from __future__ import print_function

__version__ = (0, 2, 3, "final", 0)

import collections
import os
import re
import shutil
import simplejson
import sys
import configobj

from argparse import ArgumentParser


class ClassificationConflictError(Exception):
    """
    Exception raised when one file is assigned to multiple packages
    """

    def __init__(self, pathname, packages):
        self.pathname = pathname
        self.packages = packages

    def __str__(self):
        return "Path {0!r} is assigned to multiple packages: {1}".format(
            self.pathname, ", ".join(self.packages))


class GlobPattern(object):
    """
    Pattern useful for matching files and directories.

    All characters match themselves _except_ for the following:

        '*' (single star):
        Matches any file (including no file at all)
        Equivalent to the following regular expression: '[^/]*'

        '**/' (double star followed by forward slash)
        Matches any sequence of directories (including no directories at all)
        Equivalent to the following regular expression: '(.+/|)'

    Note that matching behavior for files and directories depends on passing
    proper paths to the matcher. All directories MUST end with forward slash.

    Matching is implemented by rewriting the pattern into the equivalent
    regular expression. XXX: This is somewhat flaky as we're not really
    escaping all the features of regular expressions, just the dot and our two
    custom matchers)

    All matching is done on the full string, the pattern MUST match the whole
    pathname, not just a substring of the pathname (the regular expression is
    extended with ^...$)
    """

    # Instance cache for __new__
    __cache__ = {}

    # Instance slots
    __slots__ = ('pattern', 'compiled_pattern',)

    def __new__(cls, pattern):
        """
        Construct a new GlobPattern object if required. Reuses existing objects
        with the same pattern.
        """
        if pattern not in cls.__cache__:
            cls.__cache__[pattern] = object.__new__(cls, pattern)
        return cls.__cache__[pattern]

    def __init__(self, pattern):
        """
        Construct a GlobPattern with the specified pattern text.
        """
        self.pattern = pattern
        self.compiled_pattern = None

    def match(self, pathname):
        """
        Match pathname to the pattern.
        """
        if self.compiled_pattern is None:
            self.compiled_pattern = re.compile(
                self._translate_to_regexp(self.pattern))
        return True if self.compiled_pattern.match(pathname) else False

    @staticmethod
    def _translate_to_regexp(pattern):
        """
        Translate the pattern to regular expression.
        """
        return '^' + '(.+/|)'.join((inner.replace('*', '[^/]*') for inner in pattern.replace(".", "\.").split('**/'))) + '$'


class Package(object):
    """
    Package corresponds to entries in "packages" section of debian/split file.

    It is a named container of inclusion and exclusion patterns
    """

    def __init__(self, name, inclusion_patterns=None, exclusion_patterns=None):
        self.name = name
        self.inclusion_patterns = inclusion_patterns or []
        self.exclusion_patterns = exclusion_patterns or []

    def __contains__(self, pathname):
        """
        Check if this package should contain the specified pathname.

        Pathnames are included when they match any inclusion patterns and do
        not match any exclusion patterns.
        """
        # Note: This code micro-optimizes pattern matching by assuming that
        # most packages have many inclusion patterns and few or none exclusion
        # patterns.
        for pattern in self.inclusion_patterns:
            if pattern.match(pathname):
                break
        else:
            # If we did not match any inclusion pattern there is no point in
            # checking for exclusion patterns anymore.
            return False
        # If we match any exclusion pattern then bail out.
        for pattern in self.exclusion_patterns:
            if pattern.match(pathname):
                return False
        # By the time we got here we did match at least one inclusion pattern
        # and did not match any exclusion patterns. Therefore the package does
        # contain the specified pathname.
        return True


class FileSystemWalker(object):
    """
    Simple class that builds a list of files and directories
    """

    def __init__(self):
        self.pathnames = []

    def walk(self, topdir, remove_prefix="debian/tmp"):
        for pathname in self._walk(topdir):
            if pathname.startswith(remove_prefix):
                pathname = pathname[len(remove_prefix):]
            self.pathnames.append(pathname)
        self.pathnames.sort()

    def _walk(self, topdir):
        topdir = topdir.rstrip("/")
        yield topdir + "/"
        for root, dirs, files in os.walk(topdir):
            for dirname in dirs:
                yield os.path.join(root, dirname) + "/"
            for filename in files:
                yield os.path.join(root, filename)


class Classifier(object):
    """
    Classifier is class that can classify files to one or more packages.
    """

    def __init__(self):
        self.packages = []
        self.pathnames = []
        self.primary_package = None
        self.classifications = collections.defaultdict(set)

    def classify(self):
        """
        Classify all files to packages.

        A file may get classified to multiple packages. If you want to avoid
        this call check_conflicts() next.
        """
        for pathname in self.pathnames:
            for package in self.packages:
                if pathname in package:
                    self.classifications[pathname].add(package.name)
            if self.primary_package is not None and len(self.classifications[pathname]) == 0:
                    self.classifications[pathname].add(self.primary_package)

    def check_conflicts(self):
        """
        Check for package classification conflicts.

        If any pathname belongs to more than one package raise
        ClassificationConflictError
        """
        for pathname in self.classifications.iterkeys():
            self.__getitem__(pathname)

    def print_classification(self):
        max_len = max((len(pathname) for pathname in self.pathnames))
        for pathname in self.pathnames:
            print("{0:{1}}\t\t{2}".format(
                pathname, max_len,
                ", ".join(self.classifications[pathname])))

    def __getitem__(self, pathname):
        """
        Returns the package that this pathname is classified to
        """
        packages = self.classifications[pathname]
        if len(packages) == 1:
            return list(packages)[0]
        elif len(packages) > 1:
            raise ClassificationConflictError(pathname, packages)
        elif len(packages) == 0:
            raise KeyError(pathname)


class ConfigBase(object):

    def __init__(self):
        self.packages = []
        self.primary_package = None

    def load(self, pathname):
        raise NotImplementedError


class JSONConfig(ConfigBase):
    """
    Configuration class that reads and understand our configuration file
    """

    # JSON Schema that describes configuration files
    schema = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["dh_splitpackage 0.1"],
            },
            "packages": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "inclusion_patterns": {
                            "type": [
                                "string", {
                                    "type": "array",
                                    "items": {
                                        "type": "string"}}],
                            "optional": True},
                        "exclusion_patterns": {
                            "type": [
                                "string", {
                                    "type": "array",
                                    "items": {
                                        "type": "string"}}],
                            "optional": True}},
                    "additionalProperties": False,
                }},
            "primary_package": {
                "type": "string",
                "optional": True
            }},
        "additionalProperties": False}

    def load(self, pathname):
        with open(pathname, 'rt') as stream:
            json_data = simplejson.load(stream)
        try:
            # XXX This uses bits from linaro_json which is not widely available
            # It's still valuable if you have it as the schema validator will
            # find any accidental typos and general structure issues and give a
            # sensible error message if anything is wrong.
            from linaro_json.schema import Schema, Validator
            Validator.validate(Schema(self.schema), json_data)
        except ImportError:
            print("python-linaro-json unavailable, unable to validate "
                  "configuration file", file=sys.stderr)
        self.primary_package = json_data.get("primary_package")
        json_packages = json_data.get("packages", {})
        for package_name, json_package in json_packages.iteritems():
            json_inclusion_patterns = json_package.get("inclusion_patterns", [])
            if isinstance(json_inclusion_patterns, basestring):
                json_inclusion_patterns = [json_inclusion_patterns]
            inclusion_patterns = [
                GlobPattern(pattern) for pattern in json_inclusion_patterns]
            json_exclusion_patterns = json_package.get("exclusion_patterns", [])
            if isinstance(json_exclusion_patterns, basestring):
                json_exclusion_patterns = [json_exclusion_patterns]
            exclusion_patterns = [
                GlobPattern(pattern) for pattern in json_exclusion_patterns]
            package = Package(package_name, inclusion_patterns, exclusion_patterns)
            self.packages.append(package)


class INIConfig(ConfigBase):

    def load(self, pathname):
        config = configobj.ConfigObj(pathname)
        self.primary_package = config.get("primary_package")
        config_packages = config.get("packages", {})
        for package_name, package_section in config_packages.iteritems():
            if "inclusion_patterns" in package_section:
                inclusion_patterns = [
                    GlobPattern(pattern) for pattern in
                    package_section.as_list("inclusion_patterns")]
            else:
                inclusion_patterns = []
            if "exclusion_patterns" in package_section:
                exclusion_patterns = [
                    GlobPattern(pattern) for pattern in
                    package_section.as_list("exclusion_patterns")]
            else:
                exclusion_patterns = []
            package = Package(package_name, inclusion_patterns, exclusion_patterns)
            self.packages.append(package)


class SplitPackage(object):

    def __init__(self):
        self.parser = ArgumentParser(
            prog="dh_splitpackage",
            version="dh_splitpackage %d.%d.%d" % __version__[0:3],
            description=__doc__.split('')[0],
            epilog=__doc__.split('')[1])
        self.parser.add_argument(
            "-c", "--conf",
            default="debian/splitpackage",
            metavar="config",
            help="Use alternate configuration file")
        self.parser.add_argument(
            "--sourcedir",
            metavar="dir",
            default="debian/tmp/",
            help="Use alternate source directory")
        self.parser.add_argument(
            "-n", "--dry-run",
            action="store_true",
            default=False,
            help="Don't actually copy any files or directories")
        self.parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            default=False,
            help="Don't print the classification table")
        self.config = None
        self.classifier = Classifier()
        self.args = None

    def _load_config(self):
        try:
            config = JSONConfig()
            config.load(self.args.conf)
        except Exception as first_ex:
            try:
                config = INIConfig()
                config.load(self.args.conf)
            except:
                raise
        self.config = config
        self.config.load(self.args.conf)

    def _get_src_pathname(self, pathname):
        """
        Construct source pathname from the specified pathname

        The result should look like this:

            $SOURCEDIR/$PATHNAME

        With all the / normalized
        """
        return "/".join([
            # NOTE: We're not using os.path.join because pathnames have a
            # leading slash and os.path.join would thus discard everything
            # preceeding such a component
            self.args.sourcedir.rstrip("/"),
            pathname.lstrip("/")])

    def _get_dest_pathname(self, pathname, package):
        """
        Construct destination pathname from the specified pathname and package.

        The result should look like this
            
            debian/$PACKAGE/$PATHNAME

        Assuming that sourcedir is the default debian/tmp
        """
        return os.path.normpath(
            # NOTE: We're not using os.path.join because pathnames have a
            # leading slash and os.path.join would thus discard everything
            # preceeding such a component
            "/".join([
                self.args.sourcedir.rstrip("/"),
                "..",  # XXX: assumes debian/tmp/
                package,
                pathname.lstrip("/")]))

    def _split_package(self):
        """
        Use existing classifications to split the package
        """
        for pathname in self.classifier.pathnames:
            try:
                package = self.classifier[pathname]
            except KeyError:
                continue
            src_pathname = self._get_src_pathname(pathname)
            dest_pathname = self._get_dest_pathname(pathname, package)
            if pathname.endswith("/"):
                # Copy directory
                if not os.path.exists(dest_pathname):
                    if not self.args.quiet:
                        print("creating {0}".format(
                            dest_pathname))
                    os.makedirs(dest_pathname)
            else:
                # Copy file
                if not os.path.exists(os.path.dirname(dest_pathname)):
                    os.makedirs(os.path.dirname(dest_pathname))
                if not self.args.quiet:
                    print("copying {0} -> {1}".format(
                        src_pathname, dest_pathname))
                shutil.copy2(src_pathname, dest_pathname)

    def _find_and_classify(self):
        """
        Using existing arguments find and classify all the files in the package
        """
        walker = FileSystemWalker()
        walker.walk(self.args.sourcedir)
        self.classifier.packages = self.config.packages
        self.classifier.pathnames = walker.pathnames
        self.classifier.primary_package = self.config.primary_package
        self.classifier.classify()
        self.classifier.check_conflicts()

    def run(self):
        """
        Run dh_splitpackage
        """
        self.args = self.parser.parse_args()
        if not os.path.exists(self.args.conf):
            # Succeed silently without doing anything
            return
        try:
            self._load_config()
            self._find_and_classify()
            if not self.args.quiet:
                self.classifier.print_classification()
            if not self.args.dry_run:
                self._split_package()
        except simplejson.JSONDecodeError as ex:
            self.parser.error("%s:%d:%d %s" % (
               self.args.conf, ex.lineno, ex.colno, ex.msg))
        except configobj.ConfigObjError as ex:
            self.parser.error(str(ex))
        except ClassificationConflictError as ex:
            self.parser.error(str(ex))
        except IOError as ex:
            self.parser.error(str(ex))
