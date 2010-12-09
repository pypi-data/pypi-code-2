

from trac.core import *	#@UnusedWildImport
from trac.web.api import IRequestFilter
from trac.web.chrome import Chrome


class LoginRequiredRequestFilter(Component):
	"""Redirects all unauthenticated users to the login page without displaying nasty \"permission denied\" error messages"""
	
	implements(IRequestFilter)
	
	def pre_process_request(self, req, handler):
		"""Redirect all unauthenticated requests to the login page"""
		if req.session.authenticated or req.path_info == '/login' or handler is Chrome(self.env):
			return handler

		self.log.debug('LoginRequiredRequestFilter.pre_process_request()')
		req.redirect(req.href.login())
		return handler

	def post_process_request(self, req, template, data, content_type):
		return (template, data, content_type)
