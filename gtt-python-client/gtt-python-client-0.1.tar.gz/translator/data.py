#!/usr/bin/env python
#
# Copyright (c) 2010 oDesk corp.
#
# Licensed under terms of BSD license.
#

__author__ = 'yyurevich@jellycrystal.com (Yury Yurevich)'


import atom.core
import atom.data
import gdata.data

GTT_TEMPLATE = '{http://schemas.google.com/gtt/2009/11}%s'
GTT_TRANSLATION_STATE_TEMPLATE = ('{http://schemas.google.com/gtt/2009/11'
                                  '#translationState}%s')


class DocumentSource(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'documentSource'
    type = 'type'
    url = 'url'


class SourceLanguage(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'sourceLanguage'


class TargetLanguage(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'targetLanguage'


class Category(atom.core.XmlElement):
    _qname = GTT_TRANSLATION_STATE_TEMPLATE % 'category'
    term = 'term'
    label = 'label'


class NumberOfSourceWords(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'numberOfSourceWords'


class PercentComplete(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'percentComplete'


class TranslationMemory(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'translationMemory'
    link = atom.data.Link


class Scope(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'scope'


class Glossary(atom.core.XmlElement):
    _qname = GTT_TEMPLATE % 'glossary'
    link = atom.data.Link


class TranslationEntry(gdata.data.GDEntry, gdata.data.LinkFinder):
    _qname = atom.data.ATOM_TEMPLATE % 'entry'
    documentSource = DocumentSource
    sourceLanguage = SourceLanguage
    targetLanguage = TargetLanguage
    category = Category
    numberOfSourceWords = NumberOfSourceWords
    percentComplete = PercentComplete
    glossary = [Glossary]
    translationMemory = [TranslationMemory]


class TranslationMemoryEntry(gdata.data.GDEntry, gdata.data.LinkFinder):
    _qname = atom.data.ATOM_TEMPLATE % 'entry'
    scope = Scope


class GlossaryEntry(gdata.data.GDEntry, gdata.data.LinkFinder):
    _qname = atom.data.ATOM_TEMPLATE % 'entry'


class TranslationFeed(gdata.data.GDFeed):
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [TranslationEntry]


class TranslationMemoryFeed(gdata.data.GDFeed):
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [TranslationMemoryEntry]


class GlossaryFeed(gdata.data.GDFeed):
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [GlossaryEntry]
