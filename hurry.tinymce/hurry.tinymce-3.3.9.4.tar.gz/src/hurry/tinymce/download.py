import urllib2
import tempfile, shutil
import os

GH_URL_TEMPLATE = 'https://github.com/downloads/tinymce/tinymce/tinymce_%s.zip'
LANG_URL_TEMPLATE = ('http://www.tinymce.com/i18n/index.php?ctrl=export&'
                     'act=zip&la[]=%s&submitted=Download&pr_id=7&la_export=js')


def download_and_extract(url, callback):
    """Download zip from url and extract to temp directory.

    When downloaded, call callback with path to directory
    with an extracted tinymce. The callback will then be able to copy
    this to the appropriate location.

    """
    f = urllib2.urlopen(url)
    file_data = f.read()
    f.close()

    dir_path = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(dir_path, 'temp.zip')
        ex_path = os.path.join(dir_path, 'temp_ex')
        g = open(zip_path, 'wb')
        g.write(file_data)
        g.close()
        os.system('unzip -qq "%s" -d "%s"' % (zip_path, ex_path))
        callback(ex_path)
    finally:
        shutil.rmtree(dir_path, ignore_errors=True)


def download_tinymce(version, callback):
    """Download a tinymce of version."""
    download_and_extract(GH_URL_TEMPLATE % version, callback)


def download_language(lang, callback):
    """Download a language and add it to tinymce."""
    download_and_extract(LANG_URL_TEMPLATE % lang, callback)
