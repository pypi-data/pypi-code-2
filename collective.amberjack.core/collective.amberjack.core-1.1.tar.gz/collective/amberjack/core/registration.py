from zope.interface import classProvides
from zope.component import provideUtility
from collective.amberjack.core.interfaces import ITourDefinition
from collective.amberjack.core.interfaces import ITourRegistration
from collective.amberjack.core.tour import Tour
from cStringIO import StringIO
from urlparse import urlparse

import zipfile
import tarfile
import urllib2
import os
from translation import utils

class TourRegistration(object):
    """
    Generic tour registration class
    """
    classProvides(ITourRegistration)

    def __init__(self, source, filename=None, request=None):
        self.source = source
        if request:
            filename = self.get_filename(request)
        if not filename:
            raise AttributeError("Missing filename parameter")
        self.filename = filename

    def source_packages(self):
        raise NotImplemented

    def get_filename(self, request):
        raise NotImplemented

    def translation(self, conf):
        utils.registerTranslations(conf)

    def register(self):
        for conf in self.source_packages():
            if self.isProperTour(conf.name):
                tour = Tour(conf, self.filename)
                provideUtility(component=tour,
                               provides=ITourDefinition,
                               name=tour.tourId)
            elif conf.name.endswith(".po"):
                self.translation(conf)

    def isProperTour(self, filename):
        return filename.endswith(".cfg")

def archive_handler(filename, source):
    """ yield extracted files from a archive """

    source.seek(0)
    if filename.endswith('.zip'):
        #ZIP
        _zip = zipfile.ZipFile(source)
        for f in _zip.namelist():
            yield _zip.open(f,'r')
        
    elif filename.endswith('.tar'):
        #TAR
        _tar = tarfile.TarFile.open(fileobj=source, mode='r:')
        for f in _tar.getmembers():
            extract = _tar.extractfile(f)
            if extract:
                yield extract

    elif filename.endswith('.gz'):
        #GZ
        _tar = tarfile.TarFile.open(fileobj=source, mode='r:gz')
        for f in _tar.getmembers():
            extract = _tar.extractfile(f)
            if extract:
                yield extract

class FileArchiveRegistration(TourRegistration):
    """
    Zip archive tour registration
    """
    classProvides(ITourRegistration)

    def source_packages(self):
        _zip = StringIO()
        _zip.write(self.source)
        for archive in archive_handler(self.filename, _zip):
            yield archive

    def get_filename(self,request):
        return request.form['form.zipfile'].filename

class FolderRegistration(TourRegistration):
    """
    Folder tour registration
    """
    classProvides(ITourRegistration)

    def source_packages(self):
        for root, dirs, files in os.walk(self.filename):
            for name in files:
                file = open(os.path.join(root, name),'r')
                yield file


class WebRegistration(TourRegistration):
    """
    Web tour registration
    """
    classProvides(ITourRegistration)

    def source_packages(self):
        response = urllib2.urlopen(self.source)
        _zip = StringIO()
        _zip.write(response.read())
        for filename, archive in archive_handler(self.filename, _zip):
            yield archive

    def get_filename(self, request):
        return os.path.basename(urlparse(request.form['form.url']).path)
