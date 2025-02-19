from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array

class FEDummyResponse(ComplexModel):

	AppServer = Unicode
	DbServer = Unicode
	AuthServer = Unicode
	
	