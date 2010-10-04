from pyjon.versionning.base import Repository

class SARepository(Repository):
    def __init__(self, repo_folder, dbsession, object_classes, default_user="process"):
        self.dbsession = dbsession
        self.object_classes = object_classes
        
        super(SARepository, self).__init__(repo_folder,
                                           default_user=default_user)
    
    def get_all_objects(self):
        for objcls in self.object_classes:
            for item in self.dbsession.query(objcls):
                yield item
                
    def send_object_change(self, item):
        self.dbsession.add(item)
        self.dbsession.flush()