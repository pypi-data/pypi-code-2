# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

from lxml import etree
from django.utils.importlib import import_module
from django.conf import settings


def validate(doc):
    """
    Call all validators defined in in settings.METADATA_VALIDATORS
    on the xml given as a sttring (doc).

    Each entry in METADATA_VALIDATORS is a string with the import path
    to a callable that accepts a string as input and returns a list
    of strings describing errors, or an empty list on no errors.
    """
    try:
        validators = settings.METADATA_VALIDATORS
    except AttributeError:
        validators = []
    errors = []
    for v in validators:
        val_list = v.split('.')
        mname = '.'.join(val_list[:-1])
        cname = val_list[-1]
        module = import_module(mname)
        validator = getattr(module, cname)
        errors += validator(doc)
    return errors


# example validator function
def validate_xml_syntax(doc):
    """
    Check that the provided string contains synctactically valid xml,
    simply by trying to parse it with lxml.
    """
    try:
        etree.XML(doc)
    except etree.XMLSyntaxError, e:
        # XXX sin traducir (como traducimos e.msg?)
        error = e.msg or 'Unknown error, perhaps an empty doc?'
        return [u'XML syntax error: ' + error]
    else:
        return []
