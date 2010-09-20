#
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
from accessmanager      import CompanyAccessManager
# Comment
from create_comment     import CreateComment
from get_comment_text   import GetComment
from set_comment_text   import SetComment
from delete_comment     import DeleteComment
# Company (Contact/Enterprise operations extend these)
from get_company        import GetCompany
from create_company     import CreateCompany
from update_company     import UpdateCompany
from delete_company     import DeleteCompany
from search_company     import SearchCompany
# Address & Telephone (Company sub-components)
from get_address        import GetAddress
from create_address     import CreateAddress
from update_address     import UpdateAddress
from get_telephone      import GetTelephone
from create_telephone   import CreateTelephone
from update_telephone   import UpdateTelephone
# Assignment
from set_projects       import SetProjects
# Misc.
from keymap             import COILS_ADDRESS_KEYMAP, COILS_TELEPHONE_KEYMAP
from defaults           import COILS_DEFAULT_DEFAULTS