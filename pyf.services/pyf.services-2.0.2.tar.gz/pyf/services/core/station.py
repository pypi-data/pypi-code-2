from tg import config
from pyf.station import FlowServer
from twisted.internet import reactor
from tgscheduler import scheduler
from paste.auth import auth_tkt
from pyf.services.model import DBSession
from pyf.services.model.main import Tube
from repoze.what.predicates import NotAuthorizedError
from pyf.services.core.tasks import launch_tube
from pyf.transport.packets import Packet
import operator

def get_station_port():
    return int(config.get('station.port', '6789'))

def get_user_from_id(userid):
    return config['sa_auth'].get('user_class').by_user_name(userid)

def dispatcher(flow, client=None):
    header = flow.next()
    
    try:
        assert header.has_key('authtkt'), "No authentication data in request"        
        timestamp, userid, tokens, user_data = auth_tkt.parse_ticket(
                config.sa_auth.get('cookie_secret',
                                   'secret'),
                header.authtkt,
                '0.0.0.0')
        
        user = get_user_from_id(userid)
        permissions = map(operator.attrgetter('permission_name'),
                          user.permissions)
        
        def check_permission(perm):
            assert perm in permissions or 'manage' in permissions,\
                    'Not authorized'
        
        assert header.has_key('action'), "No action data in request"
        
        if header.action == 'launch_tube':
            check_permission('launch_tube')
            if 'object_id' in header:
                tube = DBSession.query(Tube).get(header.object_id)
            elif 'object_name' in header:
                tube = Tube.by_name(header.object_name)
            else:
                raise Exception, 'No info about which tube to launch. '\
                            'Please provide either object_id or object_name.'
            
            options = header.get('options')
            if options is not None:
                valid_options = tube.get_valid_options()
                
                for key in options:
                    if key not in valid_options:
                        raise NotAuthorizedError, "You can't set option %s" % key
            
            event_track_id, router, kwargs = launch_tube(tube.id,
                                                         user.user_name,
                                                         variant=\
                                                          header.get('variant'),
                                                         options=options,
                                                         source=flow,
                                                         only_prepare=True)
            client.message(Packet(dict(type='appinfo',
                                       key='event_track_id',
                                       value=event_track_id)))
            router.add_listener('failure', client.error)
            router.add_listener('info',
                    lambda msg, **kw: client.message(Packet(dict(type='info',
                                                                 message=msg,
                                                                 **kw))))
            router.add_listener('success',
                    lambda *a, **kw: client.success(
                    'Event %s finished successfully' % event_track_id))
            
            router.process_tube(**kwargs)
        
        else:
            raise Exception, 'Action %s unknown' % header.action
        
    except Exception, e:
        client.error(e)
        raise
    
    finally:
        for item in flow:
            pass

def init_station():
    factory = FlowServer(dispatcher)
    reactor.listenTCP(get_station_port(), factory)
    scheduler.add_single_task(reactor.run,
                              kw=dict(installSignalHandlers=0),
                              initialdelay=0)