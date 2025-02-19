from zeep import Client
from lxml import etree
from datetime import datetime
from datetime import timedelta
from Wsfe import *

# FECAEAConsultar
class FECAEAConsultar(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):
	
		periodo = '202109'
		orden = 1
		 
		print(self._client.service.FECAEAConsultar(Auth=self._auth, Periodo=periodo, Orden=orden))

