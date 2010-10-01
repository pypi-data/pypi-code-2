import logging
import os
import shutil

from mercurial import commands, hg, ui


logger = logging.getLogger("hgrecipe.recipe")


class Recipe(object):
    """
    Buildout Recipe to clone from a Mercurial Repository.

    ``location``
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
        options['location'] = options.get('location') or \
            os.path.join(buildout['buildout']['parts-directory'], name)

        self.repository = options.get('repository')
        self.location = options['location']
        self.newest = options.get('newest',
            buildout['buildout'].get('newest', 'true')).lower() != 'false'

        self.overwrite = options.get('overwrite') == 'true'

    def install(self):
        """
        Install the repository specified by the ``repository`` argument
        of the recipe.

        If it doesn't exist, clone it to the specified ``locations``,
        and if it does exist try pulling into it.

        If ``overwrite`` is marked as true in the recipe, an existing
        repositories in ``location`` will be clobbered.

        If ``overwrite`` isn't true, don't return any directories for
        Buildout to remove on uninstall.
        """
        logger.info("Cloning repository %s to %s" % (
            self.repository, self.location
        ))

        if self.overwrite:
            shutil.rmtree(self.location, ignore_errors=True)

        if not os.path.exists(self.location):
            self.clone()
        else:
            self.pull()

        if self.overwrite:
            return self.location
        return ""

    def clone(self):
        hg.clone(ui.ui(), self.repository, self.location)

    def pull(self):
        commands.pull(ui.ui(), hg.repository(ui.ui(), self.location),
            self.repository, update=True)

    def update(self):
        """
        Pull updates from the upstream repository.

        If ``newest`` is set to False in the recipe or in the buildout
        configuration, no action is taken.
        """
        if self.newest:
            logger.info("Pulling repository %s and updating %s" % (
                self.repository, self.location
            ))
            commands.pull(ui.ui(), hg.repository(ui.ui(), self.location),
                self.repository, update=True)


def uninstall(name, options):
    """
    Remove the old repository if ``overwrite`` is marked as true.
    Otherwise, leave it alone.
    """
    if options.get('overwrite') == 'true':
        shutil.rmtree(options.get('destination'), ignore_errors=True)
