# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from stellaris.dbmodels import create_db_models, Collection, User, Graph

from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed

class CollectionsFilter(object):

    def __init__(self, app, config):
        try:
            db_uri = config['store']['db_uri']
        except KeyError, e:
            raise ConfigAttributeMissing('store', str(e))

        self.__engine = create_engine(db_uri)
        
        # create the graph models using the engine, if they already exists,
        # this is ignored.
        create_collection_models(self.__engine)
                
        self.__Session = sessionmaker(bind=self.__engine, autoflush=False, transactional=False)

        self.__app = app   
        
    def __call__(self, env, resp):
        print env
        return self.app(env, resp)
