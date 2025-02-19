from zeep import Client
from Wsfe import *

# FEDummy
class FEDummy(Wsfe):

	# __init__
	def __init__(self):
		super().__init__()
		self.auth = None
	
	# run
	def run(self):
			 
		print(self._client.service.FEDummy())



