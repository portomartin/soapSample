from zeep import Client
from lxml import etree
from datetime import datetime
from datetime import timedelta
from Wsfe import *

# FECAEASinMovimientoConsultar
class FECAEASinMovimientoConsultar(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):
	
		ptoVta = 1
		cAEA = '31376603902443'
		 
		print(self._client.service.FECAEASinMovimientoConsultar(Auth=self._auth, PtoVta=ptoVta, CAEA=cAEA))

