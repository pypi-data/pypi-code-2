import zc.buildout.easy_install


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        self.executable = buildout['buildout']['executable']
        self.bin_directory = buildout['buildout']['bin-directory']
        self.eggs_directory = buildout['buildout']['eggs-directory']
        self.develop_eggs_directory = buildout['buildout']['develop-eggs-directory']
        links = buildout['buildout'].get('find-links', ())
        if links:
            links = links.split()
        self.links = links
        self.index = buildout['buildout'].get('index')
        self.newest = buildout['buildout'].get('newest') == 'true'
        self.arguments = self.options.get('arguments', '')
        self.scripts = {'createzopecoverage': self.name}

    def install(self):
        distributions = ['createzopecoverage']
        ws = zc.buildout.easy_install.install(
            distributions, self.eggs_directory,
            links=self.links,
            index=self.index,
            executable=self.executable,
            path=[self.develop_eggs_directory],
            newest=self.newest)

        return zc.buildout.easy_install.scripts(
            distributions,
            ws,
            self.executable,
            self.bin_directory,
            scripts=self.scripts,
            arguments=self.arguments,
            )

    update = install
