from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array


# ResultGet
class ResultGet(ComplexModel):
    _type_info = [
		('CAEA', Unicode),
		('Periodo', Integer),
		('Orden', Integer),
		('FchVigDesde', Unicode),
		('FchVigHasta', Unicode),
		('FchTopeInf', Unicode),
		('FchProceso', Unicode),
		# <Observaciones>
	]

class FECAEASolicitarResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ResultGet), 
		('Errors', ArrayOfErr),
		('Events', ArrayOfEvt)
    ]	
