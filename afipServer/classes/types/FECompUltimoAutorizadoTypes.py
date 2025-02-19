from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array

class FECompUltimoAutorizadoResponse(ComplexModel):

	PtoVta = Unicode
	CbteTipo = Unicode
	CbteNro = Unicode
