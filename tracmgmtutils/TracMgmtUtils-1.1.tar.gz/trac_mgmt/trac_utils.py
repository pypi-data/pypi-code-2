import ConfigParser, os
from string import Template

try:
	import sqlite3
except ImportError:
	from pysqlite2 import dbapi2 as sqlite3


class TracInstanceManager(object):
	def __init__(self, fs_path_dict, http_path_dict, base_config_file):
		self.fs_path_dict = fs_path_dict
		self.http_path_dict = http_path_dict
		self.inherit_file = base_config_file

	def get_instance(self, name):
		if self.has_instance(name):
			return TracInstance(self.fs_path_dict["trac"], self.http_path_dict, name)
		else:
			return None
	
	def get_instances(self):
		instances = []
		for dir in os.listdir(self.fs_path_dict["trac"]):
			if dir.startswith("."):
				continue
			instances.append(TracInstance(self.fs_path_dict["trac"], self.http_path_dict, dir))
		return instances
	
	def has_instance(self, name):
		return name in os.listdir(self.fs_path_dict["trac"])
	
	def new_instance(self, name, user, scm_type):
		# check for already existing instance
		if self.get_instance(name) != None:
			return None
		
		# create scm repository
		if scm_type == 'svn':
			scm_command = "svnadmin create "
		elif scm_type == 'hg':
			scm_command = "hg init "
		elif scm_type == 'git':
			scm_command = "git init --bare "
		elif scm_type == 'none':
			pass
		else:
			raise ValueError("scm_type")
		if scm_type != 'none':
			os.system(scm_command + self.fs_path_dict[scm_type] + "/" + name)
		
		# create trac instance
		if scm_type != 'none':
			os.system(Template("trac-admin $path/$name initenv $name sqlite:db/trac.db $scm $scm_path --inherit=$inherit_file").substitute(path = self.fs_path_dict["trac"], name = name, scm = scm_type, scm_path = self.fs_path_dict[scm_type] + "/" + name, inherit_file = self.inherit_file))
		else:
			os.system(Template("trac-admin $path/$name initenv $name sqlite:db/trac.db --inherit=$inherit_file").substitute(path = self.fs_path_dict["trac"], name = name, inherit_file = self.inherit_file))
		
		# create instance object
		instance = TracInstance(self.fs_path_dict['trac'], self.http_path_dict, name)
		
		# set initial plugins
		instance.add_plugin("svn_access.*")
		if scm_type == 'hg':
			instance.add_plugin("tracext.hg.*")
		elif scm_type == 'git':
			instance.add_plugin("tracext.git.*")
		instance.save()
		
		# set initial permissions
		instance.clear_user_permissions()
		instance.add_user_permission(user, "TRAC_ADMIN")
		instance.add_user_permission(user, "SCM_ACCESS")
		if "stefanc.richter" != user:
			instance.add_user_permission("stefanc.richter", "TRAC_ADMIN")
		instance.save()
		
		return instance
		
	def del_instance(self, instance):
		raise NotImplementedError()

class TracInstance(object):
	def __init__(self, fs_base_path, http_path_dict, fs_name):
		self.fs_base_path = fs_base_path
		self.http_path_dict = http_path_dict
		self.fs_name = fs_name
		
		self.path = self.fs_base_path + '/' + self.fs_name
		
		# open config
		self.config = ConfigParser.SafeConfigParser()
		self.config.read(self.path + '/conf/trac.ini')
		
		# open db
		self.db_conn = sqlite3.connect(self.path + '/db/trac.db')
	
	def __del__(self):
		self.db_conn.close()
		
	def save(self):
		# committing changes to db
		self.db_conn.commit()
		
		# saving changes to config
		configfile = open(self.path + '/conf/trac.ini', 'wb')
		self.config.write(configfile)
		configfile.close()	

	def get_name(self):
		if self.config.has_option('project', 'name'):
			return self.config.get('project', 'name')
		else:
			return ''
	def set_name(self, value):
		self.config.set('project', 'name', value)
	
	def get_description(self):
		if self.config.has_option('project', 'descr'):
			return self.config.get('project', 'descr')
		else:
			return ''
	def set_description(self, value):
		self.config.set('project', 'descr', value)
		
	def get_scm_type(self):
		if self.config.has_option('trac', 'repository_type'):
			return self.config.get('trac', 'repository_type')
		else:
			return None 
	
	def get_url(self):
		return self.http_path_dict["trac"] + '/' + self.fs_name + '/'
	
	def get_scm_url(self):
                if(self.get_scm_type()):
			return self.http_path_dict[self.get_scm_type()] + '/' + self.fs_name + '/'
		else:
			return None
		
	def get_users(self):
		"""Retrieve the users for this trac insatnce and return them in a list"""
		subjects = set([])
		groups_actions = set([])
		cursor = self.db_conn.cursor()
		cursor.execute("SELECT username, action FROM permission")
		rows = cursor.fetchall()
		for user, action in rows:
			if not user in groups_actions:
				# either a new group or a real user
				subjects.add(user)
			if action in subjects:
				# a new group
				subjects.remove(action)
			groups_actions.add(action)
		return list(subjects)
	
	def get_user_permissions(self, username):
		"""Retrieve the permissions for the given user and return them in a list."""
		subjects = set([username])
		actions = set([])
		cursor = self.db_conn.cursor()
		cursor.execute("SELECT username, action FROM permission")
		rows = cursor.fetchall()
		while True:
			num_users = len(subjects)
			num_actions = len(actions)
			for user, action in rows:
				if user in subjects:
					if action.isupper() and action not in actions:
						actions.add(action)
					if not action.isupper() and action not in subjects:
						# action is actually the name of the permission group
						# here
						subjects.add(action)
			if num_users == len(subjects) and num_actions == len(actions):
				break
		return list(actions)
	
	def clear_user_permissions(self):
		cursor = self.db_conn.cursor()
		cursor.execute("DELETE FROM permission")
	
	def add_user_permission(self, user, action):
		cursor = self.db_conn.cursor()
		cursor.execute("INSERT INTO permission VALUES (?,?)", (user, action))
	
	def get_plugins(self):
		"""Returns the enabled plugins of this instance as a list"""
		plugins = []
		
		if not self.config.has_section("components"):
			return plugins
		
		for plugin in self.config.options("components"):
			if self.config.get("components", plugin) == "enabled":
				plugins.append(plugin)
		return plugins
	
	def clear_plugins(self):
		if self.config.has_section("components"):
			self.config.remove_section("components")
		
	def add_plugin(self, name):
		if not self.config.has_section("components"):
			self.config.add_section("components")
		self.config.set("components", name, "enabled")
