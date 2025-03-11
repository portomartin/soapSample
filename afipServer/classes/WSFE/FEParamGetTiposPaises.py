from FEGetParamTypes import *

# --------------
# FEParamGetTiposPaises
# --------------
class FEParamGetTiposPaises:
	
	def __init__(self):
		None

	# run
	def run(self):

		data = (
			['1', 'Argentina'],
		)
		arr = [PaisTipo(Id=x[0], Desc=x[1]) for x in data]
		what = ArrayOfPaisTipo(PaisTipo=arr)
		# errs = ArrayOfErr(Err=[])
		# evts = ArrayOfEvt(Evt=[])
		resp = FEPaisResponse(ResultGet=what)
		return resp
		
