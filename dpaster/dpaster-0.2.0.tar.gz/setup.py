from setuptools import setup, find_packages

setup( name ="dpaster",
	version  ="0.2.0",
	packages = find_packages(),
	install_requires = ["twill","argparse"],
	scripts = ["dpaster"],
    description = "dpaster is a quick & dirty client interface to to the http://dpaste.com/ pastebin."
)
