from zeep import Client
from Wsfe import *

# FECompUltimoAutorizado
class FECompUltimoAutorizado(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):	
		
		ptoVta = 1
		cbteTipo = 1

		self.logger.info('Running FECompUltimoAutorizado')
		response = self._client.service.FECompUltimoAutorizado(Auth=self._auth, PtoVta=ptoVta, CbteTipo=cbteTipo)
		return response
