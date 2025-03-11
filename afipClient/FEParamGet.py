from zeep import Client
from Wsfe import *

# FEParamGet
class FEParamGet(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self, param):

		self.logger.info('Running ' + param)
		method_to_call = getattr(self._client.service, param)
		response = method_to_call(Auth=self._auth)
		return response
