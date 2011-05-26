'''All HTTP exceptions'''

from django.http import HttpResponse, Http404 as dHttp404

#
# 400 exceptions
#
# 400-418, 422-426
#

class Http400(Exception): pass

class Http401(Exception): pass

class Http402(Exception): pass

class Http403(Exception): pass

class Http404(dHttp404): pass

class Http405(Exception): pass

class Http406(Exception): pass

class Http407(Exception): pass

class Http408(Exception): pass

class Http409(Exception): pass

class Http410(Exception): pass

class Http411(Exception): pass

class Http412(Exception): pass

class Http413(Exception): pass

class Http414(Exception): pass

class Http415(Exception): pass

class Http416(Exception): pass

class Http417(Exception): pass

class Http418(Exception): pass

class Http422(Exception): pass

class Http423(Exception): pass

class Http424(Exception): pass

class Http425(Exception): pass

class Http426(Exception): pass

#
# 500 exceptions
#
# 500-505, 507, 509, 510
#

class Http500(Exception): pass

class Http501(Exception): pass

class Http502(Exception): pass

class Http503(Exception): pass

class Http504(Exception): pass

class Http505(Exception): pass

class Http507(Exception): pass

class Http509(Exception): pass

class Http510(Exception): pass
