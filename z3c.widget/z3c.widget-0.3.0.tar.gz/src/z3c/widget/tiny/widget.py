##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTML-Editor Widget using TinyMCE

$Id: widget.py 79769 2007-09-20 20:13:23Z srichter $
"""
__docformat__ = "reStructuredText"

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False

from zope.app.form.browser import TextAreaWidget

template = """%(widget_html)s<script type="text/javascript">
tinyMCE.init({
mode : "exact", %(options)s
elements : "%(name)s"
}
);
</script>
"""

OPT_PREFIX="mce_"
OPT_PREFIX_LEN = len(OPT_PREFIX)
MCE_LANGS=[]
import glob
import os

# initialize the language files
for langFile in glob.glob(
    os.path.join(os.path.dirname(__file__),'tiny_mce','langs') + '/??.js'):
    MCE_LANGS.append(os.path.basename(langFile)[:2])


class TinyWidget(TextAreaWidget):


    """A WYSIWYG input widget for editing html which uses tinymce
    editor.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(
    ...     form={'field.foo': u'Hello\\r\\nworld!'})

    By default, only the needed options to MCE are passed to
    the init method.

    >>> widget = TinyWidget(field, request)
    >>> print widget()
    <textarea cols="60" id="field.foo" name="field.foo" rows="15" >Hello
    world!</textarea><script type="text/javascript">
    tinyMCE.init({
    mode : "exact",
    elements : "field.foo"
    }
    );
    </script>

    All variables defined on the object which start with ``mce_`` are
    passed to the init method. Python booleans are converted
    automatically to their js counterparts.

    For a complete list of options see:
    http://tinymce.moxiecode.com/tinymce/docs/reference_configuration.html

    >>> widget = TinyWidget(field, request)
    >>> widget.mce_theme="advanced"
    >>> widget.mce_ask=True
    >>> print widget()
    <textarea ...
    tinyMCE.init({
    mode : "exact", ask : true, theme : "advanced",
    elements : "field.foo"
    }
    );
    </script>

    Also the string literals "true" and "false" are converted to js
    booleans. This is usefull for widgets created by zcml.

    >>> widget = TinyWidget(field, request)
    >>> widget.mce_ask='true'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true,
    ...
    </script>

    Languages are taken from the tiny_mce/langs directory (currently
    only the ones with an iso name are registered).

    >>> print sorted(MCE_LANGS)
    ['ar', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'fa', \
    'fi', 'fr', 'he', 'hu', 'is', 'it', 'ja', 'ko', 'nb', 'nl', \
    'nn', 'pl', 'pt', 'ru', 'si', 'sk', 'sv', 'th', 'tr', 'vi']

    If the language is found it is added to the mce options. To test
    this behaviour we simply set the language directly, even though it
    is a readonly attribute (don't try this at home)

    >>> request.locale.id.language='de'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true, language : "de",
    ...
    </script>

    """

    def __call__(self,*args,**kw):
        if haveResourceLibrary:
            resourcelibrary.need('tiny_mce')
        mceOptions = []
        for k in dir(self):
            if k.startswith(OPT_PREFIX):
                v = getattr(self,k,None)
                v = v==True and 'true' or v==False and 'false' or v
                if v in ['true','false']:
                    mceOptions.append('%s : %s' % (k[OPT_PREFIX_LEN:],v))
                elif v is not None:
                    mceOptions.append('%s : "%s"' % (k[OPT_PREFIX_LEN:],v))
        mceOptions = ', '.join(mceOptions)
        if mceOptions:
            mceOptions += ', '
        if self.request.locale.id.language in MCE_LANGS:
            mceOptions += ('language : "%s", ' % \
                           self.request.locale.id.language)
        widget_html =  super(TinyWidget,self).__call__(*args,**kw)
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "options": mceOptions}

