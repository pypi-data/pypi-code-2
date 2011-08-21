from datetime import datetime
import xmlrpclib
import logging
from grab import Grab

RPC_URL = "http://www.livejournal.com/interface/xmlrpc"


def post(login, password, subject, content):
    now = datetime.now()
    args = {
        "username" : login,
        "password" : password,
        "ver" : 1,
        "props" : {
            "opt_backdated" : False,
            "opt_preformatted" : True,
            #"taglist": ', '.join(map(str, Tag.objects.get_for_object(local_post)))
        },
        'event': content,
        'subject': subject,
        'year': now.year,
        'mon': now.month,
        'day': now.day,
        'hour': now.hour,
        'min': now.minute,
    }

    server = xmlrpclib.ServerProxy(RPC_URL)
    response = server.LJ.XMLRPC.postevent(args)
    return response.get('url')
