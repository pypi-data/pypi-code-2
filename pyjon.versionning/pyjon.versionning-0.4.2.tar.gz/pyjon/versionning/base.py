import os

from mercurial.repo import error as repo_error

from mercurial import hg, ui, commands, util

from pyjon.versionning.initialization import init_repository

import logging
logger = logging.getLogger('VERSIONNING')

import unicodedata

class Repository(object):
    def __init__(self, repo_folder, default_user="process"):
        self.repo_folder = repo_folder
        self.repo_ui = ui.ui()
        self.repo = None
        self.default_user = default_user
        self.init_repo()
        
    def init_repo(self):
        try:
            self.repo = hg.repository(self.repo_ui, self.repo_folder)
        except repo_error.RepoError:
            logger.info('Repository %s not found, creating it.' % self.repo_folder)
            init_repository(self.repo_ui, self.repo_folder)
            self.repo = hg.repository(self.repo_ui, self.repo_folder)
            logger.info('Importing initial data in repo.')
            self.store_all()
            
    def get_repo(self):
        return self.repo or hg.repository(self.repo_ui, self.repo_folder)
            
    def store_all(self):
        if hasattr(self, 'get_all_objects'):
            for item in self.get_all_objects():
                self.__store_item(item)
                        
        commands.addremove(self.repo_ui, self.repo)
        
        logger.info('Commiting initial data in repo.')
        
        commands.commit(self.repo_ui,
                        self.repo,
                        message="initial import",
                        user=self.default_user)
        
    def get_entityname(self, item):
        return str(item.__class__).split('.')[-1][:-2].lower()
    
    def get_obj_name(self, item):
        if hasattr(item, 'name'):
            return unicodedata.normalize("NFKD",
                    item.name
                    ).encode("ascii", "ignore").lower().replace(' ', '_')
        elif hasattr(item, 'display_name'):
            return unicodedata.normalize("NFKD",
                    item.display_name
                    ).encode("ascii", "ignore").lower().replace(' ', '_')
        else:
            return str(item.id)
        
    def get_filename(self, item):
        return self.get_obj_name(item) + '.xml'
    
    def get_file_content(self, item):
        if hasattr(item, 'payload_xml'):
            return item.payload_xml
        else:
            return item.payload
    
    def update_content(self, item, value):
        if hasattr(item, 'payload_xml'):
            item.payload_xml = value
        else:
            item.payload = value
    
    def get_filefolder(self, item):
        entity_folder = "%ss" % self.get_entityname(item)
        return os.path.join(self.repo_folder, entity_folder)
        
    def get_filepath(self, item):
        filename = self.get_filename(item)
        return os.path.join(self.get_filefolder(item), filename)
    
    def update_repo(self, rev=None):
        hg.update(self.repo, rev)
        
    def check_item(self, item, update=True):
        if update:
            self.update_repo()
        
        file_path = self.get_filepath(item)
        import codecs
        file_obj = codecs.open(file_path, 'rb', 'UTF-8')
        file_content = file_obj.read()
        file_obj.close()
        
        expected_file_content = self.get_file_content(item)
        
        if file_content != expected_file_content:
            self.update_content(item, file_content)
            if hasattr(self, 'send_object_change'):
                self.send_object_change(item)
            
    def store_item(self, item, user=None):
        self.__store_item(item, commit=True, user=(user or self.default_user))
        
    def delete_item(self, item, user=None):
        file_path = self.get_filepath(item)
        if os.path.exists(file_path):
            commands.remove(self.repo_ui,
                            self.repo,
                            file_path)
            commands.commit(self.repo_ui,
                            self.repo,
                            file_path,
                            message='deleting %s "%s"' % \
                                    (self.get_entityname(item),
                                     self.get_obj_name(item)),
                            user=(user or self.default_user))
        
    def __store_item(self, item, commit=False, user=None):
        file_content = self.get_file_content(item)
        file_folder = self.get_filefolder(item)
        
        if not os.path.exists(file_folder):
            os.mkdir(file_folder)
            
        file_path = self.get_filepath(item)
        
        import codecs
        f = codecs.open(file_path, 'wb', 'UTF-8')
        f.write(file_content)
        f.close()
        
        if isinstance(user, unicode):
            user = unicodedata.normalize("NFKD", user).encode("ascii", "ignore")
        
        if commit is True:
            try:
                msg = 'commiting %s - %s' % \
                                        (self.get_entityname(item),
                                         self.get_obj_name(item))
                commands.commit(self.repo_ui,
                                self.repo,
                                file_path,
                                message=str(msg),
                                user=str(user))
            except util.Abort, message:
                if u'file not tracked' in unicode(message):
                    msg = 'creating %s - %s' % \
                                            (self.get_entityname(item),
                                             self.get_obj_name(item))
                    commands.add(self.repo_ui,
                                 self.repo,
                                 file_path)
                    commands.commit(self.repo_ui,
                                    self.repo,
                                    str(file_path),
                                    message=str(msg),
                                    user=str(user))
                else:
                    raise