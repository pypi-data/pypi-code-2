from errno import EEXIST, EISDIR, ENOENT, ENOTDIR
import os
try:
    set
except NameError:
    from sets import Set as set
import urlparse

from django.conf import settings
from django.core.files.storage import Storage
from django.db import IntegrityError

from django_dbstorage.models import File


class DatabaseStorage(Storage):
    def __init__(self, location=None, base_url=None, uniquify_names=True):
        if location is None:
            location = settings.MEDIA_ROOT
        self.location = location
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.base_url = base_url
        self.uniquify_names = uniquify_names

    def _open(self, name, mode='rb'):
        name = self._name(name)
        try:
            return File.objects.open(name=name, mode=mode)
        except File.DoesNotExist:
            raise IOError(ENOENT, os.strerror(ENOENT))

    def _save(self, name, content):
        if name.endswith(os.path.sep):
            raise IOError(EISDIR, os.strerror(EISDIR))
        name = self._name(name)
        if not name:
            raise IOError(ENOENT, os.strerror(ENOENT))
        # Extract the data from content
        data = content.read()
        # Save to the database.
        while True:
            try:
                File.objects.create(name=os.path.normpath(name), data=data)
            except IntegrityError:
                # File exists. We need a new file name.
                if not self.uniquify_names:
                    raise IOError(EEXIST, os.strerror(EEXIST))
                name = self.get_available_name(name)
            else:
                # OK, the file save worked. Break out of the loop.
                break
        return name

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        name = self._name(name)
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, keep adding an underscore (before the
        # file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        while self.exists(name):
            file_root += '_'
            # file_ext includes the dot.
            name = os.path.join(dir_name, file_root + file_ext)
        return name

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        name = self._name(name)
        File.objects.filter(name=name).delete()

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        name = self._name(name)
        return bool(File.objects.filter(name=name).count())

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        path = self._name(path)
        if path and not path.endswith(os.path.sep):
            path += os.path.sep
        directories, files = set(), []
        entries = File.objects.filter(name__startswith=path)
        entries = entries.values_list('name', flat=True)
        if not entries and path:
            # Pretend empty directories don't exist, except for the root.
            raise OSError(ENOTDIR, os.strerror(ENOTDIR))
        for entry in entries:
            entry = entry[len(path):]
            bits = entry.split(os.path.sep)
            if len(bits) == 1:
                files.append(bits[0])
            else:
                directories.add(bits[0])
        # Sort the directories and files
        directories = list(directories)
        directories.sort()
        files.sort()
        return directories, files

    def _name(self, name):
        new_name = os.path.normpath(name.lstrip(os.path.sep))
        if new_name == os.path.curdir:
            return ''
        if name.endswith(os.path.sep):
            # Preserve trailing slash for directories.
            new_name += os.path.sep
        return new_name

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        return self._open(name).size

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a web browser.
        """
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')
