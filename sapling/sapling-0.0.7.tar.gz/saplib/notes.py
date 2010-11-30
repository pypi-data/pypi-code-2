import subprocess

class Notes(object):

  @classmethod
  def create(cls, repo, commit, message, ref = None):
    subprocess.Popen(["git",
                      "notes",
                      "--ref=%s" % Notes._get_ref(ref),
                      "add",
                      "--message='%s'" % message,
                      str(commit)],
                     stdout = subprocess.PIPE).communicate()[0].strip()

  @classmethod
  def has_notes(cls, remote, ref = None):
    bool(remote.repo.git.ls_remote(remote.url, Notes._get_ref(ref)))

  @classmethod
  def _get_ref(cls, ref):
    return "refs/notes/%s" % str(ref) if ref else "commits"
