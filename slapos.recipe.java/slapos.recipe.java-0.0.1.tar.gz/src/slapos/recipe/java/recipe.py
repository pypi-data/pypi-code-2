import glob
import logging
import os, sys
import shutil
import setuptools.archive_util
import zc.buildout.easy_install
import zc.buildout.download
from platform import uname
import StringIO
import subprocess
import tempfile
import gzip

JAVA_URLS = {
        'x86': "http://javadl.sun.com/webapps/download/AutoDL?BundleId=48333",
        'x86-64': "http://javadl.sun.com/webapps/download/AutoDL?BundleId=48337"
}
# XXX add more rpm platforms (HPPA, IA64, S390X, PPC)
# XXX use self-extracting packages, not rpm, to support more platforms.
# See http://java.com/en/download/manual.jsp

ARCH_MAP = {
    'i386': 'x86',
    'i586': 'x86',
    'i686': 'x86',
    'x86_64': 'x86-64'
}

ARCH_DIR_MAP = {
    'x86':'x86',
    'x86-64': 'x86_64'
}

RPM_MAGIC = '\xed\xab\xee\xdb'
GZIP_MAGIC = '\x1f\x8b'

# Took from http://ruda.googlecode.com/hg/rpm2cpio.py, BSD license
def rpm2cpio(stream_in=sys.stdin, stream_out=sys.stdout):
    lead = stream_in.read(96)
    if lead[0:4] != RPM_MAGIC:
        raise IOError, 'argument is not an RPM package'
    data = stream_in.read()
    idx = data.find(GZIP_MAGIC)
    if idx == -1:
        raise IOError, 'could not find compressed cpio archive'
    gzstream = StringIO.StringIO(data[idx:])
    gzipper = gzip.GzipFile(fileobj=gzstream)
    data = gzipper.read()
    stream_out.write(data)

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options.setdefault('cpio', 'cpio')
        options.setdefault('tmp-storage', options['location'] + '__unpack__')
        if not options.get('download-url'):
            options.setdefault('platform', self._guessPackagePlatform())
            options.setdefault(
                'flavour',
                'oracle-jdk') # or 'openjdk'
            if options['flavour'] == 'openjdk':
                raise Exception('OpenJDK is not yet supported.')
            else:
                options['download-url'] = JAVA_URLS[options['platform']]

    def _guessPackagePlatform(self):
        arch = uname()[-2]
        target = ARCH_MAP.get(arch)
        assert target, 'Unknown architecture'
        return target

    def install(self):
        location = self.options['location']
        if os.path.exists(location):
            return location
        storage = self.options['tmp-storage']
        download_file, is_temp = self.download()
        self.untar(download_file, storage)
        if is_temp:
            os.remove(download_file)
        self.unrpm(storage)
        shutil.rmtree(storage)
        return [location,]

    def download(self):
        """Download tarball. Caching if required.
        """
        url = self.options['download-url']
        namespace = self.options['recipe']
        download = zc.buildout.download.Download(self.buildout['buildout'],
                                                 namespace=namespace,
                                                 logger=self.logger)
        return download(url)

    def untar(self, download_file, storage):
        """Untar tarball into temporary location.
        """
        if os.path.exists(storage):
            shutil.rmtree(storage)
        os.mkdir(storage)
        self.logger.info("Unpacking tarball")
        os.chdir(storage)
        setuptools.archive_util.unpack_archive(
            download_file, '.')

    def unrpm(self, storage):
        """extract information from rpms into temporary location.
        """
        unrpm_dir = os.path.join(storage, 'opt')
        if os.path.exists(unrpm_dir):
            self.logger.info("Unrpm directory (%s) already exists... "
                             "skipping unrpm." % unrpm_dir)
            return
        self.logger.info("Unpacking rpms")
        os.chdir(storage)
        unpack_dir = [x for x in os.listdir('.') if os.path.isdir(x)][0]
        for path in glob.glob(os.path.join(unpack_dir, 'RPMS', '*.rpm')):
            cpio = tempfile.TemporaryFile()
            try:
              rpm = open(path)
              rpm2cpio(rpm, cpio)
              cpio.flush()
              cpio.seek(0)
              subprocess.call([self.options['cpio'], '-idum'], stdin=cpio)
            finally:
              cpio.close()
            
    def copy(self, storage):
        """Copy java installation into parts directory.
        """
        location = self.options['location']
        if os.path.exists(location):
            self.logger.info('No need to re-install java part')
            return False
        self.logger.info("Copying unpacked contents")
        java_dir = ''
        for java_dir in ('java', 'jre1.6.0_25'):
            if os.path.isdir(os.path.join(storage, 'opt', java_dir)):
                break
        assert java_dir, 'Java directory seems missing.'
        ignore_dir_list = []
        if 'ignore' in shutil.copytree.func_code.co_varnames:
            shutil.copytree(os.path.join(storage, 'opt', java_dir),
                            location,
                            ignore=lambda src,names:ignore_dir_list)
        else:
            shutil.copytree(os.path.join(storage, 'opt', java_dir),
                            location)
            for ignore_dir in ignore_dir_list:
                ignore_dir = os.path.join(location, ignore_dir)
                if os.path.exists(ignore_dir):
                    shutil.rmtree(ignore_dir)
        return True

    def update(self):
        pass
