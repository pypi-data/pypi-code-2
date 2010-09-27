#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
#
from datetime            import datetime, timedelta
from sqlalchemy          import *
from coils.core          import *
from coils.foundation    import *
from coils.logic.address import GetCompany

class GetUpcomingBirthdays(GetCompany):
    __domain__ = "contact"
    __operation__ = "get-upcoming-birthdays"
    mode = None

    def __init__(self):
        self.access_check = True
        GetCompany.__init__(self)

    def parse_parameters(self, **params):
        GetCompany.parse_parameters(self, **params)
        self.accounts = 0
        if ('accounts' in params):
            if (params.get('accounts')):
                self.accounts = 1

    def run(self):
        db = self._ctx.db_session()
        start = (datetime.now().timetuple().tm_yday - 2)
        end   = start + 15
        query = db.query(Contact).filter(and_(Contact.birth_date != None,
                                               Contact.is_account == self.accounts,
                                               Contact.status != 'archived'))
        data = [ ]
        for contact in query.all():
            if ((contact.birth_date.timetuple().tm_yday > start) and
                (contact.birth_date.timetuple().tm_yday < end)):
                data.append(contact)
        self.mode = 2
        self.set_return_value(self.add_comments(data))