from FECAEAConsultarTypes import *

# --------------
# FECAEAConsultar
# --------------
class FECAEAConsultar:
	
	def __init__(self):
		None

	# run
	def run(self):

		resultGet = ResultGet(			
			CAEA = "12345678901234", 
			Periodo = "201011", 
			Orden = 1, 
			FchVigDesde = "20101101", 
			FchVigHasta = "20101115", 
			FchTopeInf = "20101215", 
			FchProceso = "20101028"
		)
		
		errs = ArrayOfErr(Err=[])
		evts = ArrayOfEvt(Evt=[])
		resp = FECAEAConsultarResponse(ResultGet=resultGet, Errors=errs, Events=evts)
		return resp
		
