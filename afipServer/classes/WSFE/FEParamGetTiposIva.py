from FEGetParamTypes import *

# --------------
# FEParamGetTiposIva
# --------------
class FEParamGetTiposIva:
	
	def __init__(self):
		None

	# run
	def run(self):

		data = (
				 ['3', '0%', '20090220', 'NULL'],
				 ['4', '10.5%', '20090220', 'NULL'],
				 ['5', '7%', '20090220', 'NULL'],
				 ['8', '5%', '20141020', 'NULL'],
				 ['9', '2.5%', '20141020', 'NULL'],
				)

		arr = [IvaTipo(Id=v[0], Desc=v[1], FchDesde=v[2], FchHasta=v[3]) for v in data]
		ivatipos = ArrayOfIvaTipo(IvaTipo=arr)
		errs = ArrayOfErr(Err=[])
		evts = ArrayOfEvt(Evt=[])
		resp = IvaTipoResponse(ResultGet=ivatipos, Errors=errs, Events=evts)
		return resp
		
