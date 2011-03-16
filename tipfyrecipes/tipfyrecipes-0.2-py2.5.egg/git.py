# -*- coding: utf-8 -*-
# Carlo Pires <carlopires@gmail.com>
# forked from: http://pypi.python.org/pypi/hgrecipe/0.9
# Qua 16 Mar 2011 09:09:01 BRT

import logging, os, zc.buildout, subprocess

class Git(object):
	'''Simple recipe for fetch code form remote repository, using system git'''
	def __init__(self, buildout, name, options):
		self.options, self.buildout = options, buildout
		self.logger = logging.getLogger(name)

		if 'repository' not in self.options:
			raise zc.buildout.UserError('Repository url must be provided')
		self.url = options['repository']

		if 'directory' not in self.options:
			raise zc.buildout.UserError('Directory url must be provided')
		self.directory = options['directory']
		
		# ref option overrides rev
		if 'rev' in options:
			self.ref = options.get('rev', 'origin/master')
		if 'ref' in options:
			self.ref = options.get('ref', 'origin/master')

	def git(self, operation, args):
		command = ' '.join(['git', operation, '-q'] + args)
		self.logger.info(command)
		status = subprocess.call(command, shell=True)
		if status != 0:
			raise zc.buildout.UserError('Error while executing %s' % ' '.join(command))

	def install(self):
		'''Clone repository and checkout to version'''
		os.chdir(self.buildout['buildout']['directory'])
		try:
			self.git('clone', [self.url, self.directory])
			if 'rev' in self.options:
				os.chdir(self.options['directory'])
				self.git('checkout', [self.ref, ])
		except zc.buildout.UserError:
			# should manually delete files because buildout thinks that no files created
			from shutil import rmtree
			rmtree(self.options['directory'])
			raise

		os.chdir(self.buildout['buildout']['directory'])
		return self.options['directory']

	def update(self):
		'''Update repository rather than download it again'''
		os.chdir(self.options['directory'])
		self.git('fetch', ['origin', ])

		if 'rev' in self.options:
			self.git('checkout', [self.ref, ])

		os.chdir(self.buildout['buildout']['directory'])

		return self.options['directory']

def uninstall(name, options):
	"""
	Remove the old repository if ``overwrite`` is marked as true.
	Otherwise, leave it alone.
	"""
	if options.get('overwrite') == 'true':
		import shutil
		shutil.rmtree(options.get('directory'), ignore_errors=True)
