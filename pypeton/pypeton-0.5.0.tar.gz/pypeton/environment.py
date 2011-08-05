import os, os.path, random, stat
from shutil import copytree, ignore_patterns

from colors import green, yellow, COLORS

 ##### Constants #####

ROOT = os.path.abspath(os.path.dirname(__file__))
ENV_TYPES  = sorted([d for d in os.listdir(os.path.join(ROOT, 'files')) if d[0] != '.'])
FILE_TYPES = ['conf','html','ini','py','txt','types',]

 ########### Environments ###########

class Environment:
	def __init__(self, name, env, vcs_root=''):
		self.name = name
		self.env = env
		self.vcs_root = vcs_root

	def deploy(self):
		# Copy the entire directory tree over
		source = os.path.join(ROOT,'files/%s/' % self.env)
		destination = os.path.join(os.getcwd(),self.name,self.vcs_root)
		copytree(source, destination,
				ignore=ignore_patterns('*.pyc','.svn*','*.swp','.gitignore'))

		# For each file replace the keyword arguments
		for root, dirnames, filenames in os.walk(destination):
			for filename in filenames:
				parts = filename.split('.')
				extension = None
				if len(parts) >=2:
					extension = parts[-1]
				if extension and extension in FILE_TYPES:
					orig = os.path.join(root,filename)
					content = open(orig,'r').read() 
					
					context = {
						'PROJECT_NAME':self.name,
						'SECRET':'%0x'%random.getrandbits(200),
						'PROJECT_PATH':os.getcwd()
					}
					context.update(COLORS)
					file(orig, 'w').write(content % context)
		
					if filename in ['manage.py','project.py']:
						os.chmod(orig, stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)
						if filename == 'project.py':
							os.rename(orig,os.path.join(root,'%s.py'%self.name))

