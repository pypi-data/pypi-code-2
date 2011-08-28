#
# pyzmail/__init__.py
# (c) Alain Spineux <alain.spineux@gmail.com>
# http://www.magiksys.net/pyzmail
# Released under LGPL

import utils
from parse import email_address_re, PzMessage, decode_text
from generate import compose_mail, send_mail, send_mail2
from version import __version__

