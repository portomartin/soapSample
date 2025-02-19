from zeep import Client
from lxml import etree
from datetime import datetime
from datetime import timedelta
from Wsfe import *

# FECAESolicitar
class FECAESolicitar(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		
	# run
	def run(self):
	
		feCAEReq = {
		
			'FeCabReq':{			
			   'CantReg': 1, 
               'PtoVta': 1, 
               'CbteTipo': 1, 			
			}, 
			
			'FeDetReq': {			
				'FECAEDetRequest': {
					'Concepto': 1, 
					'DocTipo': 80, 
					'DocNro': '20111111112', 
					'CbteDesde': '4', 
					'CbteHasta': '4', 
					'CbteFch': '20210928', 
					'ImpTotal': 121.00, 
					'ImpTotConc': 0, 
					'ImpNeto': 100, 
					'ImpOpEx': 0, 
					'ImpTrib': 0, 
					'ImpIVA': 21,
					'MonId': 'PES',
					'MonCotiz': 1, 
					'Iva' : [
						{'AlicIva' : {
							'Id' : 5,  
							'BaseImp' 	: 100, 
							'Importe' 	: 21 
							}
						}
					]
				}
			}
		}
				 
		print(self._client.service.FECAESolicitar(Auth=self._auth, FeCAEReq=feCAEReq))



