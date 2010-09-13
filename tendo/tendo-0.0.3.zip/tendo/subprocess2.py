import subprocess

#monkeypatched_subprocess_popen = subprocess.Popen

class Popen2(subprocess.Popen):
    def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0):
		super(Popen, self).__init__()

if __name__ == '__main__':
	import subprocess
	subprocess.Popen("dir", shell=True)
	