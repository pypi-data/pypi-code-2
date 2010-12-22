# Copyright (c) 2010 by Yaco Sistemas  <lgs@yaco.es>
#
# This file is part of yaco.recipe.medialinker.
#
# yaco.recipe.medialinker is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# yaco.recipe.medialinker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with yaco.recipe.medialinker.
# If not, see <http://www.gnu.org/licenses/>.

import logging
import os.path

import pkg_resources


class MediaLinker(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        eggs_directory = self.buildout['buildout']['eggs-directory']

        media_eggs = self.options.get('media-eggs', '').split(' ')

        links = []
        destination = self._get_project_media()
        if destination is not None:
            for distribution in pkg_resources.find_distributions(eggs_directory):
                links += [self._link_media(distribution, destination)
                          for media_egg in media_eggs
                          if distribution.key == media_egg]

        links = [link for link in links if link is not None]
        return links

    def update(self):
        pass

    def _get_project_media(self):
        project_dir = os.path.join(self.buildout['buildout']['directory'],
                                   self.buildout['django']['project'])
        result = []
        os.path.walk(project_dir, find_media, result)
        if result:
            return result[0]

    def _link_media(self, distribution, destination):
        result = []
        os.path.walk(distribution.location, find_media, result)
        if result:
            source = result[0]
            destination = os.path.join(destination, distribution.key)
            if not os.path.exists(destination):
                logging.getLogger(self.name).info(
                    'Creating symbolic link from %s to %s' % (source, destination))
                os.symlink(source, destination)
            return destination
        else:
            logging.getLogger(self.name).warn(
                '%s distribution has no media directory' % distribution.key)


def find_media(result, dirname, names):
    if 'media' in names:
        result.append(os.path.join(dirname, 'media'))
        names[:] = []  # stop finding


def uninstall(name, options):
    for link in options['__buildout_installed__'].split():
        if os.path.exists(link):
            os.unlink(link)
