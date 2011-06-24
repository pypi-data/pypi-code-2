##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import shutil
import zc.buildout
import sys
import logging
import subprocess

def extension(buildout):
  Rebootstrap(buildout)()

class Rebootstrap:
  def __init__(self, buildout):
    self.logger = logging.getLogger(__name__)
    self.buildout = buildout
    # fetch section of rebootstrap, obligatory
    rebootstrap_section = buildout['rebootstrap']
    # leave garbage? only in case of developer mode
    self.developer_mode = rebootstrap_section.get('developer-mode',
      'false') == 'true'
    # fetch section to build python, obligatory
    self.python_section = rebootstrap_section['section'].strip()
    # fetch version of python build, obligatory
    version = rebootstrap_section['version'].strip()

    # usualy python will be try to found by convention in:
    # prefixed-parts/part-name/bin/part-name
    # but in case if part is non controlable it will be possible to
    # find it as
    # prefixed-parts/part-name/python-path
    # where python-path is relative path to python interpreter
    relative_python = rebootstrap_section.get('python-path', ''
      ).strip() or os.path.join('bin', self.python_section)
    # query for currently running python
    self.running_python = sys.executable

    # generate rebootstrap.realname.version
    prefix = 'rebootstrap.' + version + '.'
    self.installed = '.' + prefix + 'installed.cfg'
    self.parts_directory = os.path.join(self.buildout['buildout'][
      'directory'], prefix + 'parts')

    # query for wanted python, which is combination of suffixed parts
    # and working recipe
    self.wanted_python = os.path.join(self.parts_directory,
      self.python_section, relative_python)

    # support additional eggs
    self.eggs = []
    eggs = rebootstrap_section.get('eggs')
    if eggs:
      eggs = [q.strip() for q in eggs.split() if q.strip()]
      self.eggs = eggs

  def __call__(self):
    self.install_section()
    self.reboot()

  def reboot(self):
    if self.running_python == self.wanted_python:
      return

    message = """
************ REBOOTSTRAP: IMPORTANT NOTICE ************
bin/buildout is being reinstalled right now, as new python:
  %(wanted_python)s
is available, and buildout is using another python:
  %(running_python)s
Buildout will be restarted automatically to have this change applied.
************ REBOOTSTRAP: IMPORTANT NOTICE ************
""" % dict(wanted_python=self.wanted_python,
    running_python=self.running_python)
    self.logger.info(message)
    options = self.buildout['buildout']
    self.eggs.append('zc.buildout')
    # XXX: A lot of below code is took from zc.buildout.buildout.py:_maybe_upgrade
    # which is code duplication issue, but even if newer buildout with needed
    # hooks will be released, this extension shall work on older ones
    if zc.buildout.easy_install.is_distribute:
      self.eggs.append('distribute')
    else:
      self.eggs.append('setuptools')
    ws = zc.buildout.easy_install.install(
      [
      (spec + ' ' + options.get(spec+'-version', '')).strip()
      for spec in self.eggs
      ],
      options['eggs-directory'],
      links = options.get('find-links', '').split(),
      index = options.get('index'),
      path = [options['develop-eggs-directory']],
      prefer_final=False,
      executable=self.wanted_python
      )
    # the new dist is different, so we've upgraded.
    # Update the scripts and return True
    # Ideally the new version of buildout would get a chance to write the
    # script.  Not sure how to do that.
    partsdir = os.path.join(options['parts-directory'], 'buildout')
    if os.path.exists(partsdir):
      # This is primarily for unit tests, in which .py files change too
      # fast for Python to know to regenerate the .pyc/.pyo files.
      shutil.rmtree(partsdir)
    os.mkdir(partsdir)
    script_initialization = ''
    # (Honor the relative-paths option.)
    relative_paths = options.get('relative-paths', 'false')
    if relative_paths == 'true':
      relative_paths = options['directory']
    else:
      assert relative_paths == 'false'
      relative_paths = ''
    zc.buildout.easy_install.sitepackage_safe_scripts(
      options['bin-directory'], ws, self.wanted_python, partsdir,
      reqs=['zc.buildout'], relative_paths=relative_paths,
      include_site_packages=False,
      script_initialization=script_initialization,
      )

    # Restart
    args = map(zc.buildout.easy_install._safe_arg, sys.argv)
    # We want to make sure that our new site.py is used for rerunning
    # buildout, so we put the partsdir in PYTHONPATH for our restart.
    # This overrides any set PYTHONPATH, but since we generally are
    # trying to run with a completely "clean" python (only the standard
    # library) then that should be fine.
    env = os.environ.copy()
    env['PYTHONPATH'] = partsdir
    sys.stdout.flush()
    os.execve(self.wanted_python, [self.wanted_python] + args, env)

  def install_section(self):
    try_install = False
    try:
      if not os.path.exists(self.parts_directory) \
          or not os.path.exists(self.wanted_python):
        try_install = True
        self.logger.info('Installing section %r to provide %r in %r' % (
          self.python_section, self.wanted_python, self.parts_directory))
        args = map(zc.buildout.easy_install._safe_arg, sys.argv)
        if 'install' in args:
          args =  args[:args.index('install')]

        # remove rebootstrap extension, which is not needed in rebootstrap part
        extension_list = self.buildout['buildout']['extensions'].split()
        extension_list = [q.strip() for q in extension_list if q.strip() != \
            __name__]
        # rerun buildout with only neeeded section to reuse buildout
        # ability to calcuate all dependency
        args.extend([
          # install only required section with dependencies
          'buildout:parts=%s' % self.python_section,
          # do not load extensions (even other ones)
          'buildout:extensions=%s' % ' '.join(extension_list),
          # create virutal python environment
          'buildout:parts-directory=%s' % self.parts_directory,
          'buildout:installed=%s' % self.installed,
        ])
        self.logger.info('Rerunning buildout to install section %s with '
          'arguments %r.'% (self.python_section, args))
        process = subprocess.Popen(args)
        process.wait()
        if process.returncode != 0:
          raise zc.buildout.UserError('Error during installing python '
            'provision section.')
      if not os.path.exists(self.wanted_python):
        raise zc.buildout.UserError('Section %r directed to python executable:\n'
            '%r\nUnfortunately even after installing this section executable was'
            ' not found.\nThis is section responsibility to provide python (eg. '
            'by compiling it).' % (self.python_section, self.wanted_python))
    except zc.buildout.UserError:
      if try_install:
        if not self.developer_mode:
          if os.path.exists(self.parts_directory):
            shutil.rmtree(self.parts_directory)
          if os.path.exists(self.installed):
            os.unlink(self.installed)
        else:
          self.logger.warning('Developer mode active.')
          self.logger.warning('Directory %r and file %r are left for further '
            'analysis.' % (self.parts_directory, self.installed))
          self.logger.warning('Developer is responsible for removing those '
            'directories.')
      raise
