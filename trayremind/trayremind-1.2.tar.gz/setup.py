from distutils.core import setup
setup(
	name = 'trayremind',
	version = '1.2',
	description = 'A frontend to remind that lives in the system tray.',
	author = 'Randy Heydon',
	author_email = 'randy.heydon@clockworklab.net',
	url = 'http://randy.heydon.selfip.net/Programs/Trayremind/',
	py_modules = ['trayremind'],
	requires = ['PyGTK (>=2.10)'],
	scripts = ['trayremind']
)
