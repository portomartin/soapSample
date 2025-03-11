from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array

# FECAEASinMovimientoConsultar
class FECAEASinMovimientoConsultar(ComplexModel):
    _type_info = [
		('Ret', Unicode)
    ]
	
class FECAEASinMovimientoConsultarRequest(ComplexModel):
    
	Param = Integer
	
	
	# <CAEA>string</CAEA>
# <FchProceso>string</FchProceso>
# <Resultado>string</Resultado>
# <PtoVta>int</PtoVta>
# <Errors>
# <Err>
# <Code>int</Code>
# <Msg>string</Msg>
# </Err>
# <Err>
# <Code>int</Code>
# <Msg>string</Msg>
# </Err>
# </Errors>
# <Events>
# <Evt>
# <Code>int</Code>
# <Msg>string</Msg>
# </Evt>
# <Evt>
# <Code>int</Code>
# <Msg>string</Msg>
# </Evt>
# </Events>