#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2006-2011 Marco Pantaleoni. All rights reserved
# Marco Pantaleoni <marco.pantaleoni@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2006-2011 Marco Pantaleoni"
__license__   = "GPL v2"

import os
#import subprocess
import re
import pprint

from automa.utils import _perform_full_var_expansion
from automa.shell import sh

class ConfigEntry(object):
    """
    Abstract base class for config file entries.

    Concrete entries can be ConfigAction, ConfigValue and ConfigSection.
    """

    KIND_ACTION  = 'action'
    KIND_VALUE   = 'value'
    KIND_SECTION = 'section'

    SECTION_TYPE_SECTION = "section"

    SECTION_NAME_ROOT = "ROOT"

    def __init__(self, parent, name):
        assert '.' not in name
        self._parent = parent
        self._name   = name

    @property
    def kind(self):
        """Return one of KIND_ACTION, KIND_VALUE, KIND_SECTION."""
        return None

    @property
    def parent(self):
        """Parent ConfigEntry."""
        return self._parent

    @property
    def name(self):
        """ConfigEntry (simple) name."""
        return self._name

    @property
    def fullname(self):
        """ConfigEntry full name (with components separated by '.')."""
        r = ""
        up = self
        while up:
            if r != "":
                r += "." + qname
            else:
                r = up.name
            if up.parent is None:
                break
            up = up.parent
        return r

    @property
    def root(self):
        """Root ConfigEntry."""
        up = self
        while up:
            if up.parent is None:
                return up
            up = up.parent
        return self

    @classmethod
    def _entry_join(cls, *args):
        if (len(args) > 0) and (args[0] in ("", ConfigEntry.SECTION_NAME_ROOT)):
            args = args[1:]
        return '.'.join(args)

    @classmethod
    def _make_absolute_name(cls, section, name):
        assert isinstance(section, ConfigSection)
        if name.startswith('.'):
            if section is section.root:
                return name[1:]
            return cls._entry_join(section.fullname, name[1:])
        return name

    def __str__(self):
        return "%s" % self.fullname

    def __repr__(self):
        return "<ConfigEntry %s>" % self.fullname

class ConfigAction(ConfigEntry):
    """
    A config file 'action' entry.

    Action entries specifies actions.
    Multiple action entries with the same name can appear in the same config
    file section, and are accumulated as separate items.
    """

    def __init__(self, parent, name, value):
        super(ConfigAction, self).__init__(self, parent, name)
        self._value = value

    @property
    def kind(self):
        """Return one of KIND_ACTION."""
        return self.KIND_ACTION

    def _get_value(self):
        return self._value
    def _set_value(self, value):
        self._value = value
    value = property(_get_value, _set_value, None, "config entry value")

    def __str__(self):
        return "%s:%s" % (self.fullname, self.value)

    def __repr__(self):
        parent_name = ''
        if self.parent is not None:
            parent_name = self.parent.fullname
        return "<ConfigAction %s %s %s>" % (parent_name, self.name, self.value)

class ConfigValue(ConfigEntry):
    """
    A config file 'value' entry.

    Value entries act as sort of 'variables'.
    Each time a value of the same name is set, it replaces the previous value.

    Value entries can be present only in ConfigSection entries of type "section".
    """

    def __init__(self, parent, name, value):
        super(ConfigValue, self).__init__(self, parent, name)
        self._value = value

    @property
    def kind(self):
        """Return KIND_VALUE."""
        return self.KIND_VALUE

    def _get_value(self):
        return self._value
    def _set_value(self, value):
        self._value = value
    value = property(_get_value, _set_value, None, "config entry value")

    def __str__(self):
        return "%s=%s" % (self.fullname, repr(self.value))

    def __repr__(self):
        return "<ConfigValue [%s=%s]>" % (self.fullname, repr(self.value))

class ConfigSection(ConfigEntry):
    """
    A config file section.

    Config file section have both a section type and a section name.
    Config file sections have children entries, which can be actions, values
    and other sections.

    Only ConfigSection entries of type "section" (aka "value-section") can
    contain ConfigValue entries.

    A section can contain only a single child with the same section type and name.
    During parsing, when multiple sections with the same type and name are found,
    these are merged into one.
    """

    def __init__(self, parent, section_type, name):
        super(ConfigSection, self).__init__(self, parent, name)
        self._sec_type = section_type

        # all children (ConfigSection, ConfigValue, ConfigAction)
        self._children = []

        # ConfigValue children
        self._values         = []
        self._values_by_name = {}

    @property
    def kind(self):
        """Return KIND_SECTION."""
        return self.KIND_SECTION

    @property
    def section_type(self):
        """Section type (usually the keyword used to introduce the section)."""
        return self._sec_type

    @property
    def value_section(self):
        return (self.section_type == ConfigEntry.SECTION_TYPE_SECTION)

    def _add_entry(self, entry):
        """
        Add a child ConfigEntry.
        If the entry is a ConfigValue, it replaces an eventually existing one
        with the same name.
        """
        assert isinstance(entry, ConfigEntry)
        if entry in self._children:
            return self
        assert '.' not in entry.name
        if isinstance(entry, ConfigValue):
            if entry.name in self._values_by_name:
                for i in range(0, len(self._values)):
                    i_entry = self._values[i]
                    if i_entry.name == entry.name:
                        del self._values[i]
                        del self._values_by_name[entry.name]
                        break
            self._values_by_name[entry.name] = entry
            self._values.append(entry)

        self._children.append(entry)
        return self

    def _resolve_name(self, name, exception=True):
        """
        Resolve the given ``name``, returning the parent section and the
        corresponding entry if present (or None).

        For example, for a ``name`` of:

            abc.def.ghi

        it will return a tuple:

            (SECTION, ENTRY)

        where SECTION is the "value-section" for 'abc.def' and ENTRY is the
        ConfigEntry for its sub-entry 'ghi' (which can be either a ConfigValue
        or a ConfigSection).

        NOTE: it works only for "value-sections" (ConfigSection with type
        'section'), and for ConfigValue entries.

        ``name`` can be a full name, with separating '.'
        A leading '.' indicates a relative name (the search has to start in
        this section), otherwise the search will start from the root section.

        If ``exception`` is True, raise KeyError if no value entry with the
        given name is present.
        """
        assert self.value_section
        if name.startswith('.'):
            node = self
            name = name[1:]
        else:
            node = self.root
        while '.' in name:
            (prefix, postfix) = name.split('.', 1)
            (pfx_section, pfx_entry) = node._resolve_name(prefix, exception=exception)
            if (pfx_entry is None) or (not isinstance(pfx_entry, ConfigSection)) or (pfx_entry.section_type != ConfigEntry.SECTION_TYPE_SECTION):
                if exception:
                    raise TypeError("No suitable value section named %r" % prefix)
                return (None, None)
            assert isinstance(pfx_entry, ConfigSection)
            assert pfx_entry.value_section

            d = pfx_entry
            name = postfix
        assert isinstance(d, ConfigSection)
        assert node.value_section

        # do we have a ConfigSection entry for this name?
        for child in self._children:
            assert isinstance(child, ConfigEntry)
            if isinstance(child, ConfigSection) and child.value_section:
                if child.name == name:
                    return (node, child)

        # do we have a ConfigValue entry for this name?
        if not node._values_by_name.has_key(name):
            if exception:
                raise KeyError(ConfigEntry._make_absolute_name(node, name))
            else:
                return (node, None)
        return (node, node._values_by_name[name])

    def _value(self, name, exception=True):
        """
        Return descendant ConfigValue with the given ``name``.
        ``name`` can be a full name, with separating '.'
        A leading '.' indicates a relative name (the search has to start in
        this section), otherwise the search will start from the root section.

        If ``exception`` is True, raise KeyError if no value entry with the
        given name is present.
        """
        (section, entry) = self._resolve_name(name, exception=exception)
        if entry:
            if not isinstance(entry, ConfigValue):
                if exception:
                    raise TypeError("Entry named %r is not a value" % name)
                return None
            return entry
        return None

    def _section(self, name, exception=True):
        """
        Return descendant "value-section" ConfigSection with the given ``name``.
        ``name`` can be a full name, with separating '.'
        A leading '.' indicates a relative name (the search has to start in
        this section), otherwise the search will start from the root section.

        If ``exception`` is True, raise KeyError if no value section with the
        given name is present.
        """
        (section, entry) = self._resolve_name(name, exception=exception)
        if entry:
            if (not isinstance(entry, ConfigSection)) or (entry.sectyion_type != ConfigEntry.SECTION_TYPE_SECTION):
                if exception:
                    raise TypeError("Entry named %r is not a \"value section\"" % name)
                return None
            return entry
        return None

    def _has_value(self, name):
        v_entry = self._value(key, exception=False)
        if v_entry is not None:
            return True
        return False

    def _get_value(self, name):
        v_entry = self._value(key, exception=True)
        assert isinstance(v_entry, ConfigValue)
        return v_entry.value

    def _set_value(self, name, value):
        v_entry = self._value(name, exception=False)
        if v_entry is not None:
            assert isinstance(v_entry, ConfigValue)
            v_entry.value = value
        elif (v_entry is None) and ('.' in name):
            (prefix, postfix) = name.rsplit('.', 1)
            section = self._section(prefix, exception=True)
            assert section and isinstance(section, ConfigSection) and section.value_section
            assert '.' not in postfix
            v_entry = ConfigValue(section, postfix, value)
            section._add_entry(v_entry)
        elif (v_entry is None) and ('.' not in name):
            assert '.' not in name
            v_entry = ConfigValue(self, name, value)
            self._add_entry(v_entry)
        else:
            raise KeyError(name)
        return v_entry

    def __getitem__(self, key):
        return self._get_value(key)

    def __setitem__(self, key, value):
        self._set_value(key, value)

    def get(self, k, d=None):
        v_entry = self._value(key, exception=False)
        if v_entry is not None:
            assert isinstance(v_entry, ConfigValue)
            return v_entry.value
        return d

    def __iter__(self):
        return iter(self._children)

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value

    def items(self):
        """
        Return a list of (fullname, value) tuples for all ConfigValue entries,
        both direct and contained in sub-sections.
        """
        # only supported for "value sections"
        assert self.value_section
        items = []
        for (key, entry) in self._values_by_name.items():
            assert isinstance(entry, ConfigValue)
            items.append((entry.fullname, entry.value))
        for child in self._children:
            assert isinstance(child, ConfigEntry)
            if isinstance(child, ConfigSection) and child.value_section:
                c_items = child.items()
                items.extend(c_items)
        return items

    def __str__(self):
        import pprint
        return "%s[%s '%s']" % (self.section_type, self.fullname, pprint.pformat(self._children))

    def __repr__(self):
        import pprint
        return "<ConfigSection %s %s %s]>" % (self.section_type, self.fullname, pprint.pformat(self._children))

_NON_ID_CHAR = re.compile('[^_0-9a-zA-Z]')
def _id_mangle(text):
    """Eliminate non-allowed characters from an identifier, substituting them with '_'."""
    return _NON_ID_CHAR.sub('_', text)

_BACKTICKS_RE = re.compile('`(.*)`')

class ConfigParser:
    class LineBuffered:
        def __init__(self, fh):
            self.fh      = fh
            self.lines   = self.fh.readlines()
            self.nlines  = len(self.lines)
            self.linepos = 0
    
        def readline(self):
            if self.linepos >= self.nlines:
                return ""
            line = self.lines[self.linepos]
            self.linepos = self.linepos + 1
            return line
    
        def nextline(self, lineoffs = 0):
            lp = self.linepos + lineoffs
            if lp >= self.nlines:
                return ""
            return self.lines[lp]
    
    def __init__(self, configfile, opts=None, root=None):
        assert (root is None) or isinstance(root, ConfigSection)
        self.configfile = configfile
        self.config_fh  = None
        self.fobj       = None
        self.opts       = opts

        self.root = root or ConfigSection(parent=None, section_type=ConfigEntry.SECTION_TYPE_SECTION, name=ConfigEntry.SECTION_NAME_ROOT)

    def parse(self):
        to_close = False
        if hasattr(self.configfile, 'read'):
            self.config_fh = self.configfile
        else:
            self.config_fh = open(self.configfile, 'r')
            to_close = True
        self.fobj = ConfigParser.LineBuffered(self.config_fh)

        self._parse_section(self.root)

        if to_close:
            self.config_fh.close()
        self.config_fh = None
        self.fobj      = None
        return self.root

    def _read_ahead_tokenline(self):
        nextline = ""
        offs = -1
        while True:
            offs = offs + 1
            line = self.fobj.nextline(offs)
            if line == "":
                break
            line = line.strip()
            if len(line) < 1:
                continue
            if line[0] == "#":
                continue

            nextline = line
            break

        return nextline

    def unquote(self, a_str):
        m_v = re.match("\"(.*)\"\s*", a_str)
        if m_v:
            a_str = re.sub("\\\"", "\"", m_v.group(1))
        return a_str

    def on_section_create(self, section):
        pass

    def on_section_open(self, section):
        pass

    def on_section_close(self, section):
        pass

    def pre_action(self, section, name, value):
        return (name, value)

    def make_action_entry(self, section, name, value):
        return ConfigAction(section, name, value)

    def on_action(self, entry):
        pass

    def make_action_method_name(self, entry):
        assert isinstance(entry, ConfigAction)
        return 'handle_%s_action' % _id_mangle(entry.name))

    def pre_value(self, section, name, operator, value):
        return (name, operator, value)

    def make_value_entry(self, section, name, value):
        return ConfigValue(section, name, value)

    def on_value(self, entry):
        pass

    def _parse_section(self, section):
        assert isinstance(section, ConfigSection)
        self.on_section_open(section)
        while True:
            line = self.fobj.readline()
            if not line:
                break
            line = line.strip()
            if len(line) < 1:
                continue
            if line[0] == "#":
                continue
            while line[-1] == "\\":
                n_line = self.fobj.readline()
                if not n_line:
                    break
                n_line = line.strip()
                if len(n_line) < 1:
                    continue
                if n_line[0] == "#":
                    continue
                line = line[:-1] + n_line

            nextline = self._read_ahead_tokenline()
            nextline.strip()

            if line == '}':             # closing current section
                self.on_section_close(section)
                return

            m = re.match("^(\w+)\s*$", line)
            if m and nextline == '{':
                new_section_name = m.group(1)
                new_section = section._section(name=new_section_name, exception=False)
                if not new_section:
                    new_section = ConfigSection(parent=section, section_type=ConfigEntry.SECTION_TYPE_SECTION, name=new_section_name)
                    section._add_entry(new_section)
                    self.on_section_create(new_section)
                self._parse_section(new_section)
                continue

            m = re.match("^(\w+)\s+(\w+)\s*$", line)
            if m and nextline == '{':
                new_section_type = m.group(1)
                new_section_name = m.group(2)
                new_section = None
                if (new_section_type == ConfigEntry.SECTION_TYPE_SECTION):
                    new_section = section._section(name=new_section_name, exception=False)
                if not new_section:
                    new_section = ConfigSection(parent=section, section_type=new_section_type, name=new_section_name)
                    section._add_entry(new_section)
                    self.on_section_create(new_section)
                self._parse_section(new_section)
                continue

            m = re.match("^([a-zA-Z0-9_\.:/\?\~\!\@\#\$\%\^\&\+\|\-]+)\s*(\+=|=)\s*(.*)", line)
            if m:
                (key, operator, value) = m.groups()
                (key, operator, value) = self.pre_value(section, key, operator, value)
                (entry_section, entry) = self._resolve_name(key, exception=False)
                if (entry_section is None) or (not isinstance(entry_section, ConfigSection)) or (entry_section.section_type != ConfigEntry.SECTION_TYPE_SECTION):
                    raise TypeError("%r is not in a \"value section\"" % key)
                assert isinstance(entry_section, ConfigSection) and entry_section.value_section
                assert (entry is None) or isinstance(entry, ConfigValue)
                #(done, value) = self.expandcmd(value)
                if _BACKTICKS_RE.match(value):
                    m = _BACKTICKS_RE.match(value)
                    cmdline = m.group(1)
                    value = sh(cmdline, capture=True, configsection=section)
                else:
                    value = self.unquote(value)
                    value = _perform_full_var_expansion(value, vars=self.opts, configsection=section)
                if operator == '+=':
                    if entry is not None:
                        assert isinstance(entry, ConfigValue)
                        value = entry.value + value
                        entry.value = value
                    else:
                        entry = section._set_value(key, value)
                elif operator == '=':
                    if entry is not None:
                        assert isinstance(entry, ConfigValue)
                        entry.value = value
                    else:
                        entry = section._set_value(key, value)
                self.on_value(entry)
                continue

            m = re.match("^([a-zA-Z0-9_]+)\s+(.*)", line)
            if m:
                (key, value) = m.groups()
                (key, value) = self.pre_action(section, key, value)
                #(done, value) = self.expandcmd(value)
                if _BACKTICKS_RE.match(value):
                    m = _BACKTICKS_RE.match(value)
                    cmdline = m.group(1)
                    value = sh(cmdline, capture=True, configsection=section)
                else:
                    value = self.unquote(value)
                    value = _perform_full_var_expansion(value, vars=self.opts, configsection=section)
                entry = self.make_action_entry(section, key, value)
                section._add_entry(entry)
                self.on_action(entry)
                action_method_name = self.make_action_method_name(entry)
                method = getattr(self, action_method_name, None)
                if method and callable(method):
                    method(entry)
                continue

        # -- end of 'while True:'

        # fall-off (EOF)
        self.on_section_close(section)

class IncludeConfigParser(ConfigParser):
    """A ConfigParser that handles 'include' actions."""

    def resolve_include_path(self, includepath):
        return includepath

    def handle_include(self, entry):
        assert isinstance(entry, ConfigAction)
        pathname = self.resolve_include_path(entry.value)
        cparser = IncludeConfigParser(pathname, opts=self.opts, root=self.root)
        cparser.parse()
        return self
