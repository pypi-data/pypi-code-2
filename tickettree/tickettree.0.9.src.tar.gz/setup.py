from setuptools import setup

setup(
    name='TicketTree',
    version='0.9',
    packages=['tickettree'],
    package_data={'tickettree' : ['*.txt', 'templates/*.html', 'htdocs/*.*', 'htdocs/js/*.js', 'htdocs/css/*.css', 'htdocs/images/*.*']},
    author = 'Roberto Longobardi, Marco Cipriani',
    author_email='seccanj@gmail.com',
    license='BSD. See the file LICENSE.txt contained in the package.',
    url='http://trac-hacks.org/wiki/TicketTree',
    download_url='https://sourceforge.net/projects/tickettree4trac/files/',
    description='Ticket Tree',
    long_description='A Trac plugin to display tickets in a tree, organized based on structured ticket titles.',
    keywords='trac plugin ticket tree organization structure',
    entry_points = {'trac.plugins': ['tickettree = tickettree']}
    )
