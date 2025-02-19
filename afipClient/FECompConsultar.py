from zeep import Client
from Wsfe import *

# FECompConsultar
class FECompConsultar(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):	
		
		feCompConsReq = {	
		   'CbteTipo': 1, 			
		   'CbteNro': 1, 
		   'PtoVta': 1
		}
		
		self.logger.info('Running FECompConsultar')
		response = self._client.service.FECompConsultar(Auth=self._auth, FeCompConsReq = feCompConsReq)
		return response
