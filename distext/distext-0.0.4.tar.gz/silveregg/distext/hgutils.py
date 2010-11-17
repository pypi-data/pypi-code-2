import subprocess
import warnings

def get_hg_version(branch=None):
    if branch is None:
        p = subprocess.Popen(["hg", "branch"], stdout=subprocess.PIPE)
        stdout = p.communicate()[0]
        if not p.returncode == 0:
            raise ValueError("Error while running hg branch: %s" % stdout)
        branch = stdout.strip()
    cmd = ["hg", "head", "-r", branch, "--template", "{node}"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = p.communicate()[0]
    if not p.returncode == 0:
        raise ValueError("Error while running hg (cmd: %s)" % " ".join(cmd))
    return stdout

def generate_hg_version(version, is_released, target):
    try:
        hg_version = get_hg_version()
    except (OSError, ValueError), e:
        warnings.warn("Could not get hg revision (%s)" % str(e))
        hg_version = "unavailable"

    fid = open(target, "w")
    try:
        fid.write("""\
released = %s
version = '%s'
hg_version = '%s'
""" % (is_released, version, hg_version))
    finally:
        fid.close()

