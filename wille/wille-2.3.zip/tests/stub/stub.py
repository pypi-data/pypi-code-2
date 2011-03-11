import wille

class StubService(wille.Service):
	def execute(self, params, servicepool, keyring, workdir):
		return ""
