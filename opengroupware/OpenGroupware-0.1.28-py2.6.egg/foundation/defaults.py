# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

COILS_DEFAULT_DEFAULTS = {
    'LSConnectionDictionary': { 'databaseName': 'OGo',
                                'hostName': '127.0.0.1',
                                'password': '',
                                'port': 5432,
                                'userName': 'OGo' },
    'LSDisableEnterpriseProjectCreate': 'YES',
    'AMQConfigDictionary': { 'hostname': '127.0.0.1',
                             'port': 5672,
                             'username': 'guest',
                             'password': 'guest' },
    'LSAttachmentPath': '/var/lib/opengroupware.org/documents',
    'SkyPublicExtendedPersonAttributes': [ { 'key': "email1", 'type': 3 },
                                           { 'key': "email2", 'type': 3 },
                                           { 'key': "email3", 'type': 3 },
                                           { 'key': "job_title" },
                                           { 'key': "other_title1" },
                                           { 'key': "other_title2" }
    ],
    'SkyPrivateExtendedPersonAttributes': [ ],
    'SkyPublicExtendedEnterpriseAttributes': [ { 'key': "email2", 'type': 3 },
                                               { 'key': "email3", 'type': 3 },
                                               { 'key': "job_title" },
                                               { 'key': "other_title1" },
                                               { 'key': "other_title2" }
    ],
    'SkyPrivateExtendedEnterpriseAttributes': [],
    'LSAutoCompanyLoginPrefix': 'OGo',
    'LSAutoCompanyNumberPrefix': 'OGo',
    'LSDisableSessionLog':  False,
    'OGoTeamCreatorRoleName': 'team creators',
    'PYTrustedHosts': [''],
    'LSCalendars': [ ],
    'zOGIExpandAllIntranet': False,
    'OIEProcessDebugEnabled': True,
    'CoilsExtensionMIMEMap': { 'pdf': 'application/pdf' }
    }