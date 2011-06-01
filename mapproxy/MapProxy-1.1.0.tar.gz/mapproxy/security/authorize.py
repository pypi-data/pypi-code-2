# import pprint
# from repoze.what.predicates import has_permission, is_anonymous, NotAuthorizedError
# 
# class Authorize(object):
#     def __init__(self, app, global_conf):
#         self.app = app
#     def __call__(self, environ, start_reponse):
#         if not 'repoze.what.adapters' in environ:
#             return self.app(environ, start_reponse)
#         
#         adapters = environ['repoze.what.adapters']
#         permission_adapters = adapters['permissions']
#         
#         
#         # pprint.pprint(environ)
#         try:
#             has_permission('wms').check_authorization(environ)
#         except NotAuthorizedError:
#             if is_anonymous(environ):
#                 start_reponse("401 Unauthorized", {})
#                 return ['auth required']
#             start_reponse("403 Forbidden", {})
#             return ['forbidden']
#         
#         print has_permission('wms').is_met(environ)
#         # if 'REMOTE_USER' not in environ:
#             # start_reponse("401 Unauthorized", {})
#             # return ['auth required']
#         return self.app(environ, start_reponse)



class SimpleAuthFilter(object):
    def __init__(self, app, global_conf):
        self.app = app
    
    def __call__(self, environ, start_reponse):
        environ['mapproxy.authorize'] = self.authorize
        return self.app(environ, start_reponse)
    
    def authorize(self, service, layers=[], **kw):
        if service.startswith('wms.'):
            auth_layers = {}
            allowed = denied = False
            for layer in layers:
                if layer.startswith('secure'):
                    auth_layers[layer] = {}
                    allowed = True
                else:
                    auth_layers[layer] = {
                        'map': True,
                        'featureinfo': False,
                        'legendgraphic': True,
                    }
                    denied = True
                
        if allowed and not denied:
            return {'authorized': 'full'}
        if denied and not allowed:
            return {'authorized': 'none'}
        return {'authorized': 'partial', 'layers': auth_layers}

# def authorize(service, layers=None):
#     
#     
#     
#     authorize('wms'):
#     {'authorized': 'true'}
#     
#     
#     
#     authorize('wms.capabilities'):
#     {'authorized': 'partial'}
#     
#     authorize('wms.capabilities', layers=['layer1', 'layer2']):
#     {
#         'authorized': 'partial',
#         'layers': {
#             'layer1': {
#                 'featureinfo': False,
#                 'map': True,
#                 'legend': False},
#             },
#            'layer2': {
#                 'featureinfo': False,
#                 'map': True,
#                 'legend': False},
#             },
#     }
#     
#     authorize('kml'):
#     {'authorized': 'false'}
#     
# 
#     authorize('wms.map', layers=['layer1', 'layer2']):
#     {
#         'authorized': 'partial',
#         'layers': {
#             'layer1': {
#                 'featureinfo': False,
#                 'map': True,
#                 'legend': False},
#             },
#            'layer2': {
#                 'featureinfo': False,
#                 'map': True,
#                 'legend': False},
#             },
#     }
# 
# 
#     
#     {'authorized': 'true'}
#     {'authorized': 'false'}
#     
#     {'authorized': 'partial',
#      'layers': {
#         'layer1': { 'featureinfo': False,
#                     'map': True,
#                     'legend': False},
#                     
#      }
#     }
#     return {'authorized': }