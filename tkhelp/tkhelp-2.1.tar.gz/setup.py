from distutils.core import setup

setup(
    name = "tkhelp",
    version = "2.1",
    author = "maik Woehl",
    author_email = "logander4@icqmail.com",
    url = "http://www.daemon-tuts.de/blog",
    description = "tkhelp is a german help program. Is implemented a GUI with many Tk-Widgets and a Webinterface, that is easy to update.",
    long_description = "The GUI is a small collection of Tk-Widget descriptions. In the Webinterface you can see many examples and a great description, because the GUI is only updated in the stable releases(1.0,1.5,2.0,2.5,...).",
    data_files = ['test.gif', 'webinterface/tkhelp.db', 'webinterface/conf/update.sh', 'webinterface/conf/backup.sh', 'webinterface/conf/createDB.sh'],
    py_modules = ['tkhelp', 'tkh_splash3', 'tkhelp_lang_de', 'dt_tkobjects', 'webinterface/server', 'webinterface/conf/write', 'webinterface/getcontent'],
    classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: GUI",
    "Environment :: Web Environment",]
    
)
