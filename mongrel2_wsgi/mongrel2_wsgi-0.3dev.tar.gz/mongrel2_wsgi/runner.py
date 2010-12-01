# -*- coding: utf-8 -*-

def server_runner(wsgi_app, global_conf, **kwargs):
    """Paste Deploy entry point for .ini configuration."""
    import mongrel2_wsgi.server
    # kwargs keys chosen to match Handler() in the server config:
    server = mongrel2_wsgi.server.Mongrel2WSGIServer(
            wsgi_app, 
            sender_id=kwargs['send_ident'], 
            sub_addr=kwargs['send_spec'], 
            pub_addr=kwargs['recv_spec']
            )
    server.start()

