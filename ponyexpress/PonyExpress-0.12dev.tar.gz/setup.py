from distutils.core import setup

setup(
    name='PonyExpress',
    version='0.12dev',
		author = 'Tony Landis',
		author_email = 'tony.landis@gmail.com',
    packages=['ponyexpress',],
		scripts=['ponyexpress/*','manage.py','default_settings.cfg','run_gearman.py'],
		url = 'https://github.com/tony-landis/PonyExpress',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
		install_requires=[
			'Flask',
			'Flask-Actions',
			'gearman',
			'formencode',
			'couchdbkit',
		]
)
