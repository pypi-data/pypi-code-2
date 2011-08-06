# Carlo Pires <carlopires@gmail.com>
# Seg 14 Mar 2011 21:46:55 BRT 
import logging, os, zc.buildout

class CreateSymbolicLinks:
	"""
	Buildout recipe for create dir and link modules. Use as:

	[buildout]
	parts = 
		django
		tipfy

	[django]
	recipe = recipes:ln
	target = /home/carlo/django/trunk/django
	directory = app/lib/dist/django

	[tipfy]
	recipe = recipes:ln
	directory = app/lib/dist
	target = /home/carlo/tipfy/tipfy
	target_names = 
		tipfy
		tipfyext


	"""
	def __init__(self, buildout, name, options):
		self.name, self.options = name, options
		self.logger = logging.getLogger(self.name)

		if 'directory' not in self.options:
			raise zc.buildout.UserError('Link directory must be provided')
		self.directory = self.options['directory']

		if 'target' not in self.options:
			raise zc.buildout.UserError('Target directory must be provided')
		self.target = self.options['target']

		if 'target_names' in self.options:
			self.targets = [s.strip() for s in self.options['target_names'].split('\n') if len(s) > 0]
		else:
			self.targets = None

	def create_symbolic_link(self, target, directory):
		if not os.path.exists(os.path.dirname(directory)):
			os.makedirs(os.path.dirname(directory))
		if not os.path.exists(directory):
			target = os.path.realpath(target)
			self.logger.info('Creating symbolic link %s -> %s', directory, target)
			os.symlink(target, directory)

	def install(self):
		if self.targets:
			for link_name in self.targets:
				target = os.path.join(self.target, link_name)
				directory = os.path.join(self.directory, link_name)
				self.create_symbolic_link(target, directory)
		else:
			self.create_symbolic_link(self.target, self.directory)

		return self.targets or self.target

	def update(self):
		pass

def uninstall(name, options):
	logger = logging.getLogger(name)

	if 'directory' not in options:
		raise zc.buildout.UserError('Link directory must be provided')
	directory = options['directory']

	if 'target' not in options:
		raise zc.buildout.UserError('Target directory must be provided')
	target = options['target']

	if 'target_names' in options:
		targets = [s.strip() for s in options['target_names'].split('\n') if len(s) > 0]
	else:
		targets = None

	if targets:
		for link_name in targets:
			path = os.path.join(directory, link_name)
			try:
				os.readlink(path)
				os.unlink(path)
			except:
				pass
	else:
		try:
			os.readlink(directory)
			os.unlink(directory)
		except:
			pass

