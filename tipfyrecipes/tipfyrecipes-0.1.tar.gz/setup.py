from setuptools import setup, find_packages

setup(
    name = 'tipfyrecipes',
    version = '0.1',
    license = 'BSD',
    keywords='buildout recipe google app engine appengine gae zc.buildout tipfy',
    url='http://code.google.com/p/tipfyrecipes/',
    description = 'Buildout recipes for Tipfy web framework',
    author = 'Carlo Pires',
    author_email = 'carlopires@gmail.com',
    zip_safe = False,
    platforms = 'any',
    packages = find_packages(),
    install_requires=[
        'setuptools',
        'zc.buildout >= 1.5.2',
        'z3c.recipe.scripts >= 1.0.1',
        'Mercurial',
        'Mock==0.6.0',
    ],
	entry_points = {
		'zc.buildout': [
			'sdk = tipfyrecipes.gae.sdk:InstallGAE',
			'tools = tipfyrecipes.gae.tools:InstallGAETools',
			'applib = tipfyrecipes.gae.applib:InstallAppLib',
			'git = tipfyrecipes.git:Git',
			'hg = tipfyrecipes.hg:Mercurial',
			'svn = tipfyrecipes.svn:Subversion',
			'ln = tipfyrecipes.ln:CreateSymbolicLinks',
		],
		'zc.buildout.uninstall': [
			'git = tipfyrecipes.git:uninstall',
			'hg = tipfyrecipes.hg:uninstall',
			'svn = tipfyrecipes.svn:uninstall',
			'ln = tipfyrecipes.ln:uninstall',
		],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
