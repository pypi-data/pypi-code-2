#!/usr/bin/python
# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
MF = MessageFactory('dolmen.widget.file')

from dolmen.widget.file.widget import (
    IFileWidget, FileWidget, DisplayFileWidget, FileSchemaField)
