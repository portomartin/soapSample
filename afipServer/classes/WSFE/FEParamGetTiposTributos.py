from FEGetParamTypes import *

# --------------
# FEParamGetTiposTributos
# --------------
class FEParamGetTiposTributos:
	
	def __init__(self):
		None

	# run
	def run(self):

		data = (
				 ['1', 'Impuestos nacionales', '20100917', 'NULL'],
				 ['2', 'Impuestos provicinciales', '20100917', 'NULL'],
				 ['3', 'Impuestos municipales', '20100917', 'NULL'],
				 ['4', 'Impuestos Internos', '20100917', 'NULL'],
				 ['99', 'Otro', '20100917', 'NULL'],
				)

		arr = [TributoTipo(Id=x[0], Desc=x[1], FchDesde=x[2], FchHasta=x[3]) for x in data]
		what = ArrayOfTributoTipo(TributoTipo=arr)
		errs = ArrayOfErr(Err=[Err(Msg="Hola", Code='2')])
		evts = ArrayOfEvt(Evt=[Evt(Msg="Hola", Code='2')])
		resp = FETributoResponse(ResultGet=what, Errors=errs, Events=evts)
		return resp
		
