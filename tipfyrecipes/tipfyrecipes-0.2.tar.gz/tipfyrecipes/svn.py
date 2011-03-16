# -*- coding: utf-8 -*-
# Carlo Pires <carlopires@gmail.com>
# borrowed from: http://pypi.python.org/pypi/iwm.recipe.svncheckout/0.0.1
# Ter 15 Mar 2011 14:01:03 BRT 
import logging, os
import pkg_resources

import zc.buildout
import zc.recipe.egg

from subprocess import Popen, PIPE

def cmd(cmdline):
	p = Popen(cmdline.split(), stdout=PIPE)
	return p.communicate()[0]

class Subversion:
	def __init__(self, buildout, name, options):
		self.name, self.options = name, options
		self.logger = logging.getLogger(self.name)
		self.root_directory = buildout['buildout']['directory']

		self.target = os.path.join(self.root_directory, options['directory'])

		options.setdefault('revision', 'HEAD')
		self.revision = options.get('revision')

		self.url = options['url']
		self.newest = (
			buildout['buildout'].get('offline', 'false') == 'false' and \
			buildout['buildout'].get('newest', 'true') == 'true'
		)

	def update(self):
		"""
		Does nothing if buildout is in offline mode.
		"""
		if not self.newest:
			return self.target

		os.chdir(self.target)
		update_command = 'svn up -r %s' % self.revision
		self.logger.info(update_command)
		cmd(update_command)

		return self.target

	def install(self):
		"""
		Checkout a working copy. Fails if buildout is
		running in offline mode.
		"""
		os.chdir(self.root_directory)
		install_command = 'svn co -r %s %s %s' % (self.revision, self.url, self.target)
		self.logger.info(install_command)
		cmd(install_command)
		return self.target

def uninstall(name, options):
	"""
	Remove the old repository if ``overwrite`` is marked as true.
	Otherwise, leave it alone.
	"""
	if options.get('overwrite') == 'true':
		import shutil
		shutil.rmtree(options.get('directory'), ignore_errors=True)
