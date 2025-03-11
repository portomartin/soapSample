from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array

from FEGetParamTypes import *

# FECAEAConsultarResponse
class ResultGet(ComplexModel):
    _type_info = [
		('CAEA', Unicode),
		('Periodo', Integer),
		('Orden', Integer),
		('FchVigDesde', Unicode),
		('FchVigHasta', Unicode),
		('FchTopeInf', Unicode),
		('FchProceso', Unicode),
	]


class FECAEAConsultarResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ResultGet), 
		('Errors', ArrayOfErr),
		('Events', ArrayOfEvt)
    ]
	


# <soapenv:Envelope
		# xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
		# xmlns:ar="http://ar.gov.afip.dif.FEV1/">
	# <soapenv:Header/>
	# <soapenv:Body>
		# <ar:FECAEAConsultar>
			# <ar:Auth>
				# <ar:Token>string</ar:Token>
				# <ar:Sign>string</ar:Sign>
				# <ar:Cuit>long</ar:Cuit>
			# </ar:Auth>
			# <ar:Periodo>int</ar:Periodo>
			# <ar:Orden>short</ar:Orden>
		# </ar:FECAEAConsultar>
	# </soapenv:Body>
# </soapenv:Envelope>

class FECAEAConsultarRequest(ComplexModel):
    
	Param = Integer
