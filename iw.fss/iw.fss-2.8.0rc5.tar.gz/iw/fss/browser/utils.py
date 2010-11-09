# -*- coding: utf-8 -*-
# $Id: utils.py 117088 2010-05-07 15:26:09Z glenfant $
"""Misc utilities"""

from StringIO import StringIO
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from iw.fss.FileSystemStorage import FileSystemStorage

class FilesFinder(BrowserView):
    """Finds all files of fields of the context object
    """
    def __call__(self):
        out = StringIO()
        print >> out, "FSS storage information for this item"
        context = aq_inner(self.context)
        try:
            schema = context.Schema()
        except AttributeError, e:
            print >> out, "Issue: This item is not an AT based content"
        else:
            fieldnames_with_fss = [f.__name__ for f in schema.fields()
                                   if isinstance(f.storage, FileSystemStorage)]
            for name in fieldnames_with_fss:
                field = context.getField(name)
                fss_info = field.storage.getFSSInfo(name, context)
                fss_strategy = field.storage.getStorageStrategy(name, context)
                try:
                    fss_props = field.storage.getStorageStrategyProperties(name, context, fss_info)
                except AttributeError:
                    # In case of empty field
                    print >> out, "Field '%s' is empty thus stored in no file" % name
                else:
                    path = fss_strategy.getValueFilePath(**fss_props)
                    print >> out, "Field '%s' is in %s" % (name, path)
            if len(fieldnames_with_fss) == 0:
                print >> out, "No field uses FSS on this item"
        return out.getvalue()
