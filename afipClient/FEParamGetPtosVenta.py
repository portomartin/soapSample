from zeep import Client
from Wsfe import *

# FEParamGetPtosVenta
class FEParamGetPtosVenta(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):	
		
		self.logger.info('Running FEParamGetPtosVenta')
		response = self._client.service.FEParamGetPtosVenta(Auth=self._auth)
		return response
