# -*- coding: utf-8 -*-
# Carlo Pires <carlopires@gmail.com>
# forked from: http://pypi.python.org/pypi/hgrecipe/0.9
# Qua 16 Mar 2011 09:09:01 BRT
import logging
import os
import shutil

from mercurial import commands, hg, ui

class Mercurial(object):
	"""
	Buildout Recipe to clone from a Mercurial Repository.

	``directory``
		The file path where the repository will be cloned to. Defaults
		to a folder matching the name of the repository in the Buildout
		parts directory.

	``repository``
		The url of the repository to clone.

	``newest``
		Whether to pull updates from the source repository during
		subsequent Buildouts. This can be specified on the recipe or
		at the Buildout level.

	``overwrite``
		Whether to clobber an existing repository on install and have
		Buildout remove on uninstallation or to keep it around always.
	"""

	def __init__(self, buildout, name, options):
		options['directory'] = options.get('directory') or \
			os.path.join(buildout['buildout']['parts-directory'], name)

		self.logger = logging.getLogger(name)

		self.repository = options.get('repository')
		self.directory = options['directory']
		self.newest = options.get('newest',
			buildout['buildout'].get('newest', 'true')).lower() != 'false'

		self.overwrite = options.get('overwrite') == 'true'

	def install(self):
		"""
		Install the repository specified by the ``repository`` argument
		of the recipe.

		If it doesn't exist, clone it to the specified ``directorys``,
		and if it does exist try pulling into it.

		If ``overwrite`` is marked as true in the recipe, an existing
		repositories in ``directory`` will be clobbered.

		If ``overwrite`` isn't true, don't return any directories for
		Buildout to remove on uninstall.
		"""
		self.logger.info("Cloning repository %s to %s" % (
			self.repository, self.directory
		))

		if self.overwrite:
			shutil.rmtree(self.directory, ignore_errors=True)

		if not os.path.exists(self.directory):
			self.clone()
		else:
			self.pull()

		if self.overwrite:
			return self.directory
		return ""

	def clone(self):
		hg.clone(ui.ui(), self.repository, self.directory)

	def pull(self):
		commands.pull(ui.ui(), hg.repository(ui.ui(), self.directory),
			self.repository, update=True)

	def update(self):
		"""
		Pull updates from the upstream repository.

		If ``newest`` is set to False in the recipe or in the buildout
		configuration, no action is taken.
		"""
		if self.newest:
			self.logger.info("Pulling repository %s and updating %s" % (
				self.repository, self.directory
			))
			commands.pull(ui.ui(), hg.repository(ui.ui(), self.directory),
				self.repository, update=True)

def uninstall(name, options):
	"""
	Remove the old repository if ``overwrite`` is marked as true.
	Otherwise, leave it alone.
	"""
	if options.get('overwrite') == 'true':
		shutil.rmtree(options.get('directory'), ignore_errors=True)
